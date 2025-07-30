import logging
from logging.handlers import QueueListener
import hashlib
import datetime
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Optional, List
from watchtower_logging import config
from watchtower_logging.version import __version__

class WatchtowerHandler(logging.Handler):

    """
    A logging handler that sends logs to a Watchtower endpoint
    """

    def __init__(self, 
                 beam_id: str,
                 host: str,
                 token: Optional[str] = None,
                 protocol: str = 'https', 
                 retry_count: int = config.DEFAULT_RETRY_COUNT,
                 backoff_factor: int = config.DEFAULT_BACKOFF_FACTOR,
                 use_fallback: bool = True,
                 fallback_host: Optional[str] = None,
                 dedup: bool = True,
                 dedup_keys: Optional[List[str]] = None,
                 http_timeout: int = config.DEFAULT_HTTP_TIMEOUT,
                 dev: bool = False) -> None:

        super().__init__()

        self.beam_id = beam_id
        self.host = host
        self.token = token
        self.protocol = protocol
        self.http_timeout = http_timeout
        self.retry_count = retry_count
        self.backoff_factor = backoff_factor
        self.dedup = dedup
        self.dedup_keys = dedup_keys
        self.dev = dev

        self.use_fallback = use_fallback
        self.fallback_host = fallback_host or 'fallback.' + self.host

        # prevent infinite recursion by silencing requests and urllib3 loggers
        self._silence_loggers()

        self.session = self._setup_session()

    @classmethod
    def for_django(cls) -> 'WatchtowerHandler':

        """
        Create a WatchtowerHandler instance configured by Django settings.

        This method reads Watchtower-specific settings from the Django configuration and
        returns a WatchtowerHandler instance with those settings applied.
        """

        from django.conf import settings

        token = getattr(settings, 'WT_TOKEN', None)
        protocol = getattr(settings, 'WT_PROTOCOL', config.DEFAULT_DJANGO_PROTOCOL)
        retry_count = getattr(settings, 'WT_NUM_RETRY', config.DEFAULT_DJANGO_NUM_RETRY)
        backoff_factor = getattr(settings, 'WT_BACKOFF_FACTOR', config.DEFAULT_DJANGO_BACKOFF_FACTOR)
        use_fallback = getattr(settings, 'WT_USE_FALLBACK', config.DEFAULT_DJANGO_USE_FALLBACK)
        fallback_host = getattr(settings, 'WT_FALLBACK_HOST', config.DEFAULT_DJANGO_FALLBACK_HOST)
        dedup = getattr(settings, 'WT_DEDUP', config.DEFAULT_DJANGO_DEDUP)
        dedup_keys = getattr(settings, 'WT_DEDUP_KEYS', config.DEFAULT_DJANGO_DEDUP_KEYS)
        http_timeout = getattr(settings, 'WT_HTTP_TIMEOUT', config.DEFAULT_DJANGO_HTTP_TIMEOUT)
        django_debug = getattr(settings, 'DEBUG', config.DEFAULT_DJANGO_DEV)
        dev = getattr(settings, 'WT_DEV', django_debug)

        return cls(
            beam_id=settings.WT_BEAM_ID,
            host=settings.WT_HOST,
            token=token,
            protocol=protocol,
            retry_count=retry_count,
            backoff_factor=backoff_factor,
            use_fallback=use_fallback,
            fallback_host=fallback_host,
            dedup=dedup,
            dedup_keys=dedup_keys,
            http_timeout=http_timeout,
            dev=dev)

    def _silence_loggers(self) -> None:

        """
        Prevent infinite recursion by silencing some loggers that 
        are used by the handler itself
        """

        for logger_name in ['requests', 'urllib3', __name__]:
            logging.getLogger(logger_name).propagate = False

    def formatTime(self, 
                   record: logging.LogRecord, 
                   datefmt: Optional[str] = None) -> str:

        """
        Format the time of a log record.

        :param record: The log record containing the creation time.
        :param datefmt: Optional format string for the date.
        :return: Formatted time string.
        """

        ct = datetime.datetime.fromtimestamp(record.created, tz=datetime.timezone.utc)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S%z")
            s = "%s,%03d" % (t, record.msecs)
        return s

    def build_frame_info(self,
                         record: logging.LogRecord) -> Dict[str, Any]:

        """
        Build a dictionary containing frame information from a log record.

        :param record: The log record to extract frame information from.
        :return: A dictionary with filename, line number, and function name.
        """

        return {
            'filename': record.pathname,
            'lineno': record.lineno,
            'function': record.funcName
        }
    
    def generate_dedup_id(self,
                          payload: dict) -> str:
    
        """
        Method to generate a deduplication id for a log message
        """

        data = payload.get('data', {})

        # If dedup_keys are specified, use them to filter extra data for generating the dedup ID
        if not self.dedup_keys is None and isinstance(self.dedup_keys, (list, tuple, set)):
            
            dedup_data = {k:v for k,v in payload.items() if k in self.dedup_keys and k != 'data'}
            if data:
                dedup_data['data'] = {k: v for k, v in data.items() if k in self.dedup_keys}
            
        else:
            # Otherwise, include all extra data and add the message
            dedup_data = payload

        return hashlib.md5(json.dumps(dedup_data,
                                    sort_keys=True,
                                    indent=None,
                                    separators=(',',':')).encode('utf-8')).hexdigest()

    def build_payload(self,
                      record: logging.LogRecord) -> dict:

        """
        Build the payload that is sent in the http request.

        :param record: The log record to build the payload from.
        :return: A dictionary representing the payload.
        """

        if not hasattr(record, 'asctime'):
            record.asctime = self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%f%z")

        if not hasattr(record, 'dev'):
            record.dev = self.dev

        payload = {
            'asctime': record.asctime,
            'name': record.name,
            'levelname': record.levelname,
            'message': record.getMessage(),
            'dev': record.dev,
            'taskName': record.taskName,
            'execution_id': record.execution_id,
            'beam_id': self.beam_id,
            'frame__': self.build_frame_info(record)}
        
        if hasattr(record, 'env') and record.env:
            payload['env__'] = record.env

        if hasattr(record, 'levelno'):
            payload['severity'] = int(record.levelno)

        data = {k:v for k,v in record.__dict__.items() if not k in payload
                and not k in ('msg','args','levelno','pathname','filename','module','exc_info',
                              'exc_text', 'stack_info', 'lineno', 'funcName', 'created', 'msecs', 
                              'relativeCreated', 'thread', 'threadName', 'processName', 'process', 
                              'data', 'env', 'wt_extra_data')}

        if hasattr(record, 'data') and record.data:
            data = {**data, **record.data}
        else:
            record.data = {}

        payload['data'] = data

        if self.dedup:
            dedup_id = self.generate_dedup_id(payload)
            record.dedup_id = dedup_id
            payload['dedup_id'] = dedup_id

        return payload
    
    def build_params(self,
                     record: logging.LogRecord) -> dict:
        
        """
        Build the url query parameters dictionary that is sent in the http request.

        :param record: The log record to build the parameters from.
        :return: A dictionary representing the parameters.
        """

        params = {
            'lvl': record.levelname,
            'exec_id': record.execution_id,
            't': record.asctime }
        
        if self.dedup:
            params['dedup'] = record.dedup_id
    
        return params

    def prepareRecord(self,
                      record: logging.LogRecord) -> logging.LogRecord:
        
        """
        Prepare the log record by building its payload and parameters
        and attaching them to the record as attributes.

        :param record: The log record to prepare.
        :return: The modified log record with payload and parameters 
        as attributes, called payload and params.
        """

        record.payload = self.build_payload(record)
        record.params = self.build_params(record)

        return record
        
    def _setup_session(self) -> requests.Session:

        """
        Set up a requests session with retry logic.
        """
        
        session = requests.Session()
        retries = Retry(total=self.retry_count, backoff_factor=self.backoff_factor, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def handle(self, 
               record) -> logging.LogRecord | bool:
        
        """
        Handle the log record by preparing it (by calling prepareRecord) 
        and then calling the parent class's handle method.

        :param record: The log record to handle.
        :return: The prepared log record or False if the record is filtered.
        """

        record = self.prepareRecord(record)
        return super().handle(record)

    def emit(self,
             record: logging.LogRecord) -> None:
        
        """
        Emit the log record by sending it to the HTTP endpoint.

        :param record: The log record to emit.
        """
        
        try:
            # Send the log entry to the HTTP endpoint
            self.send_log(payload=record.payload, params=record.params)
        except Exception as e:
            print(f"Failed to send log entry: {e}")

    def send_log(self, 
                 payload: Dict[str, Any],
                 params: Dict[str, Any]) -> None:
        
        """
        Send the log entry to the HTTP endpoint.

        :param payload: The payload dictionary to send.
        :param params: The parameters dictionary to send.
        """

        headers = {'User-Agent': self.user_agent}
        if self.token:
            headers['Authorization'] = self.auth_header

        try:
            response = self.session.post(self.url, json=payload, headers=headers, params=params, timeout=self.http_timeout)
            response.raise_for_status()

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:

            if self.use_fallback:
                self._send_fallback(payload, headers)
            else:
                raise e
            
        except requests.exceptions.HTTPError as e:

            if response.status_code >= 500 and self.use_fallback:
                self._send_fallback(payload, headers)
            else:
                raise e
            
    def _send_fallback(self, 
                       payload: Dict[str, Any], 
                       headers: Dict[str, str]) -> None:
        
        """
        Send the log entry to the fallback HTTP endpoint.

        :param payload: The payload dictionary to send.
        :param headers: The headers dictionary to send.
        """
        
        response = self.session.post(self.fallback_url, json=payload, headers=headers, timeout=self.http_timeout)
        response.raise_for_status()

    def build_endpoint(self,
                       host: str) -> str:
        
        """
        Build the endpoint URL for the given host.

        :param host: The host to build the endpoint for.
        :return: The endpoint URL.
        """

        return f'{self.protocol}://{host}/api/beams/{self.beam_id}'
    
    @property
    def user_agent(self) -> str:
        
        """
        Get the user agent string, representing the Watchtower logging library version.

        :return: The user agent string.
        """

        return config.USER_AGENT_STR_FMT.format(version=__version__)

    @property
    def auth_header(self) -> str:

        """
        Build the authentication header
        """

        return f'Token {self.token}'

    @property
    def url(self) -> str:

        """
        Get the URL of the HTTP endpoint.

        :return: The URL of the HTTP endpoint.
        """

        return self.build_endpoint(host=self.host)
    
    @property
    def fallback_url(self) -> str:

        """
        Get the URL of the fallback HTTP endpoint.

        :return: The URL of the fallback HTTP endpoint.
        """

        return self.build_endpoint(host=self.fallback_host)

class WatchtowerInternalHandler(WatchtowerHandler):

    """
    Handler class that sends events directly to a Splunk endpoint,
    bypassing the Watchtower Queue. Use only for interal Watchtower processes
    that otherwise could cause a error loop in the queue.
    """

    def __init__(self, 
                 host: str,
                 token: str,
                 protocol: str = 'https',
                 retry_count: int = config.DEFAULT_RETRY_COUNT,
                 backoff_factor: int = config.DEFAULT_BACKOFF_FACTOR,
                 http_timeout: int = config.DEFAULT_HTTP_TIMEOUT,
                 dev: bool = False,
                 index: str = config.WATCHTOWER_INTERNAL_INDEX) -> None:
        
        self.index = index

        super().__init__(beam_id = '_internal',
                         host=host,
                         token=token,
                         protocol=protocol,
                         retry_count=retry_count,
                         backoff_factor=backoff_factor,
                         use_fallback=False,
                         fallback_host=None,
                         dedup=False,
                         dedup_keys=None,
                         http_timeout=http_timeout,
                         dev=dev)
        
    @classmethod
    def for_django(cls):

        raise NotImplementedError
    
    def generate_dedup_id():

        raise NotImplementedError
    
    def send_log(self, 
                 payload: Dict[str, Any],
                 params: Dict[str, Any]) -> None:
        
        """
        Send the log entry to the HEC endpoint.

        :param payload: The payload dictionary to send.
        :param params: The parameters dictionary to send.
        """

        headers = {'User-Agent': self.user_agent}
        if self.token:
            headers['Authorization'] = self.auth_header

        event = {
            **self.default_meta,
            'event': payload
        }

        try:
            response = self.session.post(self.url, json=event, headers=headers, timeout=self.http_timeout)
            response.raise_for_status()

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:

            print('Connection for internal logging request to Splunk failed ' + str(e))
            
        except requests.exceptions.HTTPError as e:

            print('Internal logging request to Splunk failed ' + str(e))
    
    @property
    def default_meta(self) -> Dict[str, str]:

        return {
            'index': self.index,
            'source': 'watchtower_internal_logging',
            'sourcetype': '_json',
            'host': 'internal'
        }

    @property
    def user_agent(self) -> str:
        
        """
        Get the user agent string, representing the Watchtower logging library version.

        :return: The user agent string.
        """

        return config.USER_AGENT_STR_FMT.format(version=__version__) + '/internal'
    
    @property
    def auth_header(self) -> str:

        """
        Build the authentication header
        """

        return f'Splunk {self.token}'
    
    def build_endpoint(self,
                       host: str) -> str:
        
        """
        Build the endpoint URL for the given host.

        :param host: The host to build the endpoint for.
        :return: The endpoint URL.
        """

        return f'{self.protocol}://{host}/services/collector/event'


class CustomQueueListener(QueueListener):

    def stop(self, 
             timeout: Optional[float] = None) -> None:

        """
        Stop the listener.

        This asks the thread to terminate, and then waits for it to do so.
        Note that if you don't call this before your application exits, there
        may be some records still left on the queue, which won't be processed.
        """

        if self._thread:  # see gh-114706 - allow calling this more than once
            self.enqueue_sentinel()
            self._thread.join(timeout)  # Wait for the thread to finish
            self._thread = None