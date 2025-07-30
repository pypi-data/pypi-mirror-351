from enum import IntEnum
import logging
import os
import platform
import subprocess
from packaging.requirements import Requirement
from typing import Optional, Literal, Callable, List, Dict
import sys
import traceback
from functools import wraps
import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from itertools import accumulate as _accumulate, repeat as _repeat
from bisect import bisect as _bisect
import random
import warnings

from watchtower_logging import config
from watchtower_logging.version import __version__

class logLevels(IntEnum):

    """
    Custom enumeration of logging levels, including both standard
    and watchtower-defined levels (start and done) 
    START and DONE are meant for scheduled functions that we want to monitor and detect if they ran at all (START) 
    and finished correctly (DONE).
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    START = config.START_LEVEL_NUM
    DONE = config.DONE_LEVEL_NUM
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

def get_cf_name() -> str | None:
    
    """
    Try to get the Cloud function name from environment variables that 
    specify the name of a Google Cloud function. Returns None if not found.
    """

    return os.environ.get('K_SERVICE') or os.environ.get('FUNCTION_NAME')

def build_logger_name(name: str) -> str:
    
    """
    Build the logger name using a given name or environment variables that specify the name of a Google Cloud function.
    Fall back to the default logging name config.DEFAULT_LOGGER_NAME
    """

    return (
        name or 
        get_cf_name() or 
        config.DEFAULT_LOGGER_NAME)

def parse_requirements(input: str) -> List[dict]:

    """
    Parse requirements from a string input into a list of dictionaries containing package names and versions.
    """

    requirements = [Requirement(t) for t in input.strip().split('\n')]
    return [
        {
            'name': req.name,
            'version': req.specifier.__str__()[2:] if req.specifier.__str__().startswith('==') else req.specifier.__str__()
        } for req in requirements
    ]

def get_environment() -> Dict:

    """
    Returns environment information including Python version and installed packages.
    """

    env = {'lng': 'Python'}

    try:
        env['lng_version'] = platform.python_version()
    except Exception:
        pass

    try:
        result = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE, text=True)
        requirements_from_pip = parse_requirements(result.stdout)
    except Exception as e:
        return env

    try:
        with open(os.path.join(os.getcwd(), 'requirements.txt'), 'r') as f:
            x = f.read()
        requirement_names_from_file = [req['name'] for req in parse_requirements(x)]
    except Exception as e:
        return env

    env['packages'] = [req for req in requirements_from_pip if req['name'].lower() in requirement_names_from_file]

    return env

def monitor_func(logger,
                 func_name: Optional[str] = None,
                 set_execution_id: bool = True,
                 execution_id: Optional[str] = None,
                 start_done: bool = True,
                 except_level: Literal[*logLevels._member_names_] = 'ERROR',
                 reset_default_data: bool = True) -> Callable:
    
    """
    A decorator to monitor and log the execution of a function, handling both normal execution and exceptions.

    Parameters:
        logger (WatchtowerLogger): The logger instance used for logging.
        func_name (Optional[str], optional): A custom name for the function being monitored. If not provided, the function's actual name (`__name__`) will be used.
        set_execution_id (bool, optional): Whether to set a unique execution ID before the function is executed. Defaults to True.
        execution_id (Optional[str], optional): A specific execution ID to set. If not provided, one will be generated automatically.
        start_done (bool, optional): If True, logs "START" and "DONE" messages before and after function execution. Defaults to True.
        except_level (Literal[*logLevels._member_names_], optional): The log level to use for exceptions (e.g., "ERROR", "CRITICAL"). Defaults to 'ERROR'.
        reset_default_data (bool, optional): Whether to reset the logger's default data to its initial state before function execution. Defaults to True.

    Returns:
        Callable: The wrapped function with monitoring and logging behavior.

    Description:
        - This decorator wraps a function to:
          1. Optionally log a "START" message before execution.
          2. Execute the function.
          3. Optionally log a "DONE" message upon successful completion.
        - If an exception is raised:
          - Logs the exception at the specified level (`except_level`).
          - Optionally returns a pre-defined object (`return_when_exception`) or an HTTP 500 error response
            when the environment variable `FUNCTION_SIGNATURE_TYPE` is set to http (in Google Cloud functions).
            Otherwise, returns None
    """


    # Decorator to monitor function execution, logging start and done events and handling exceptions.
    def decorator(func):

        @wraps(func) # Preserve the wrapped function's metadata
        def wrapper(*args, **kwargs):
            
            """
            The actual wrapper function that handles logging and exception management.
            """

            fname = func_name or func.__name__

            try:
                # Set the execution ID if required
                if set_execution_id:
                    logger.setExecutionId(execution_id)

                # Reset logger's default data if required
                if reset_default_data:
                    logger.setDefaultData(data=logger.init_default_data or {}, 
                                          overwrite=True)
                
                # Check if threading is enabled in a Google Cloud function. If so, issue a warning
                if logger.use_threading and not get_cf_name() is None:
                    warnings.warn('You are using a Google Cloud Function but have threading enabled. This may not work as intended.', UsageWarning)
                    logger.warning('You are using a Google Cloud Function but have threading enabled. This may not work as intended.')

                # Log the "START" message if start_done is True
                if start_done:
                    logger.start(f'Starting {fname}')

                # Execute the wrapped function
                result = func(*args, **kwargs)

                # Log the "DONE" message if start_done is True
                if start_done:
                    logger.done(f'Done with {fname}')                    

                return result # Return the result of the wrapped function

            except Exception as e:
                
                # Log the exception at the specified level with traceback details
                getattr(logger, except_level.lower())(
                    str(e), data={'traceback': traceback.format_exc(),
                                    'exc_info': traceback.format_exc()}
                )

                # Return a pre-configured object if specified
                if hasattr(logger, 'return_when_exception'):
                    return logger.return_when_exception
                
                # If running in an HTTP environment in a Google cloud function, return a 500 response
                elif os.getenv('FUNCTION_SIGNATURE_TYPE') == 'http':
                    return ({'details': 'Server Error'}, 500)

        return wrapper

    return decorator

def send_alert(logger,
               alert_token: str,
               name: str,
               lead: str,
               body: str = '',
               details: str = '',
               priority: bool = False,
               level: str = 'alert',
               dev: Optional[bool] = None,
               min_time: Optional[datetime.datetime] = None,
               max_time: Optional[datetime.datetime] = None,
               search_time: Optional[datetime.datetime] = None,
               link_text: Optional[str] = None,
               link_url: Optional[str] = None,
               docs_text: Optional[str] = None,
               docs_url: Optional[str] = None,
               alert_update_url: Optional[str] = None,
               retry_count: int = config.DEFAULT_ALERT_RETRY_COUNT,
               backoff_factor: int = config.DEFAULT_ALERT_BACKOFF_FACTOR,
               timeout: int = config.DEFAULT_ALERT_HTTP_TIMEOUT):

    """
    Send an alert using HTTP POST to https://alert.<watchtower_host>, where <watchtower_host>
    is defined when instantiating the logger.

    Parameters:
        logger (WatchtowerLogger): The logger instance.
        alert_token (str): Alert token for Watchtower beam. Must be a valid string of length > 10.
        name (str): The name of the alert, providing a concise summary.
        lead (str): A lead or headline for the alert, providing context or a key message.
        body (str, optional): Detailed information about the alert. Defaults to an empty string.
        details (str, optional): Additional details to be included in the alert. Defaults to an empty string.
        priority (bool, optional): Whether the alert is of high priority. Defaults to False.
        dev (Optional[bool], optional): Development mode flag. Defaults to the logger's `dev` setting if not provided.
        min_time (Optional[datetime.datetime], optional): The minimum time for the event being alerted about. Must be a `datetime` instance if provided.
        max_time (Optional[datetime.datetime], optional): The maximum time for the event being alerted about. Must be a `datetime` instance if provided.
        search_time (Optional[datetime.datetime], optional): The time the alert is associated with. Defaults to the current UTC time.
        link_text (Optional[str], optional): Text for a hyperlink included in the alert. Defaults to None.
        link_url (Optional[str], optional): URL for the hyperlink. Required if `link_text` is provided.
        docs_text (Optional[str], optional): Text for a documentation link. Defaults to None.
        docs_url (Optional[str], optional): URL for the documentation link. Required if `docs_text` is provided.
        alert_update_url (Optional[str], optional): URL to update the alert dynamically if needed. Defaults to None.
        retry_count (int, optional): Number of retries for the HTTP request in case of failure. Defaults to `config.DEFAULT_ALERT_RETRY_COUNT`.
        backoff_factor (int, optional): Backoff factor for retry logic. Defaults to `config.DEFAULT_ALERT_BACKOFF_FACTOR`.
        timeout (int, optional): Timeout for the HTTP request. Defaults to `config.DEFAULT_ALERT_HTTP_TIMEOUT`.

    Description:
        - Constructs a JSON payload (`alert_body`) containing the alert information.
        - Validates critical fields such as `alert_token`, `search_time`, and optional fields like `min_time` and `max_time`.
        - Allows customization of the alert with links (`link_url` and `link_text`) or documentation references (`docs_url` and `docs_text`).
        - Uses an HTTP session with retry logic to send the alert to a server.
        - Logs a critical error to Watchtower with the alert body and traceback if the alert cannot be sent successfully.
    """

    alert_body = None

    try:

        # Determine the development mode if not explicitly provided
        dev = dev if isinstance(dev, bool) else logger.dev

        # Validate the alert token
        assert isinstance(alert_token, str) and len(alert_token) > 10, 'Invalid alert token'

        # Validate the level
        assert level in ('alert', 'info', 'warning'), f'Invalid alert level {level}'

        # Ensure search_time is a valid datetime, default to current UTC time if not provided
        if search_time is None:
            search_time = datetime.datetime.now(datetime.timezone.utc) 
        assert isinstance(search_time, datetime.datetime), 'search_time needs to be a datetime instance'

        # Build the intial alert body
        alert_body = {
            'name': name,
            'lead': lead,
            'body': body,
            'details': details,
            'level': level, # Always set the level to "alert"
            'priority': priority,
            'dev': dev,
            'info_search_time': search_time.timestamp()
        }

        # Add optional minimum and maximum time fields, validating their types
        if not min_time is None:
            assert isinstance(min_time, datetime.datetime), 'min_time needs to be a datetime instance'
            alert_body['info_min_time'] = min_time.timestamp()

        if not max_time is None:
            assert isinstance(max_time, datetime.datetime), 'max_time needs to be a datetime instance'
            alert_body['info_max_time'] = max_time.timestamp()

        # Add optional hyperlink details if provided
        if not link_url is None:
            link = {'url': link_url}
            if not link_text is None:
                link['text'] = link_text
            alert_body['link'] = link

        # Add optional documentation details if provided
        if not docs_url is None:
            docs = {'url': docs_url}
            if not docs_text is None:
                docs['text'] = docs_text
            alert_body['docs'] = docs

        # Include an alert update URL if specified
        if not alert_update_url is None:
            alert_body['alert_update_url'] = alert_update_url

        # Construct the alerting endpoint URL
        url = 'https://alerts.' + logger.host

        # Define the request headers for authentication and user-agent identification
        headers = {'Authorization': alert_token,
                   'User-Agent': config.USER_AGENT_STR_FMT.format(version=__version__)}

        # Set up an HTTP session with retry logic
        session = requests.Session()
        retry = Retry(total=retry_count,
                      backoff_factor=backoff_factor,
                      status_forcelist=[500, 502, 503, 504])

        # Attach the retry logic to the session
        session.mount(url, HTTPAdapter(max_retries=retry))
        # Send the POST request with the alert body
        r = session.post(url,
                         json=alert_body,
                         headers=headers,
                         timeout=timeout)
        r.raise_for_status() # Raise an exception for non-2xx status codes

    except Exception as e:

        logger.critical('Failed to send alert',
                        data={
                            'alert_body': alert_body,
                            'error': str(e),
                            'traceback': traceback.format_exc()})
        
def random_choices(population: List, 
                   weights: Optional[List] = None, 
                   *, 
                   cum_weights: Optional[List] = None, 
                   k: int = 1) -> List:

    """
    Return a k sized list of population elements chosen with replacement.
    If the relative weights or cumulative weights are not specified,
    the selections are made with equal probability.
    """

    if hasattr(random, 'choices'):
        return random.choices(population=population, weights=weights, cum_weights=cum_weights, k=k)

    n = len(population)
    if cum_weights is None:
        if weights is None:
            _int = int
            n += 0.0    # convert to float for a small speed improvement
            return [population[_int(random.random() * n)] for i in _repeat(None, k)]
        cum_weights = list(_accumulate(weights))
    elif weights is not None:
        raise TypeError('Cannot specify both weights and cumulative weights')
    if len(cum_weights) != n:
        raise ValueError('The number of weights does not match the population')
    bisect = _bisect
    total = cum_weights[-1] + 0.0   # convert to float
    hi = n - 1
    return [population[bisect(cum_weights, random.random() * total, 0, hi)]
            for i in _repeat(None, k)]

def attach_watchtower_exception_hook(logger: logging.Logger) -> None:

    """
    Attaches a global exception handler to the logger to log unhandled exceptions.
    """

    def watchtower_handle_exception(exc_type, exc_value, exc_traceback):

        if issubclass(exc_type, KeyboardInterrupt):

            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical('Uncaught Exception', data={'traceback': '{exc_type}: {exc_value}\n{traceback}'.format(exc_type=exc_type.__name__,
                                                                                                                exc_value=exc_value,
                                                                                                                traceback=''.join(traceback.format_tb(exc_traceback)))})
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = watchtower_handle_exception

# Custom warning type for protocol-related issues, is not filtered by default
class ProtocolWarning(Warning): pass

# Custom warning type when we detect non best practice usage
class UsageWarning(Warning): pass