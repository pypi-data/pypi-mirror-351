
import logging
import queue
import atexit
import warnings
from logging.handlers import QueueHandler
from typing import Optional, List

from watchtower_logging import utils, config
from watchtower_logging.loggers import WatchtowerLogger
from watchtower_logging.handlers import WatchtowerHandler, CustomQueueListener, WatchtowerInternalHandler

def getLogger(beam_id: str,
              host: str,
              name: Optional[str] = None, 
              execution_id: Optional[str] = None, 
              token: Optional[str] = None, 
              protocol: str = 'https', 
              dev: bool = False, 
              default_data: Optional[dict] = None,
              level: int = utils.logLevels.START, 
              debug: Optional[bool] = None, 
              path: Optional[str] = None, 
              console: bool = False, 
              send: bool = True, 
              use_threading: bool = True, 
              dedup: bool = True,
              dedup_keys: Optional[List] = None, 
              retry_count: int = config.DEFAULT_RETRY_COUNT,
              backoff_factor: float = config.DEFAULT_BACKOFF_FACTOR,
              catch_all: bool = True, 
              dedup_id_key: Optional[str] = None, 
              use_fallback: bool = True,
              fallback_host: Optional[str] = None,
              lvl_frame_info: Optional[int] = None,
              env_interval: int = config.DEFAULT_ENV_INTERVAL,
              internal: Optional[bool] = False) -> logging.Logger:
    
    """
    Create and configure a Watchtower logger. This function is the main entrypoint for logging to Watchtower.

    Args:
        beam_id (str): Unique identifier for the beam.
        host (str): Host for sending log data.
        name (Optional[str]): Name of the logger. Defaults to a cloud function name (if available) and 'watchtower-logging' otherwise.
        execution_id (Optional[str]): Execution id for the logger. Will default to a random string of config.EXECUTION_ID_LENGTH characters.
        token (Optional[str]): Authentication token for the beam. Defaults to None.
        protocol (str): Protocol to use ('http' or 'https'). Defaults to 'https'. http only allowed in development mode
        dev (bool): Flag to indicate development environment. Defaults to False.
        default_data (Optional[dict]): Default data to include in each log entry. Defaults to None.
        level (int): Logging level. Defaults to utils.logLevels.START.
        debug (bool): Flag to enable debug mode (no longer supported). Defaults to None.
        path (Optional[str]): File path for logging (no longer supported). Defaults to None.
        console (bool): Flag to add console handler. Defaults to False.
        send (bool): Flag to send logs to the endpoint. Defaults to True.
        use_threading (bool): Flag to enable threading for logging. Defaults to True.
        dedup (bool): Flag to enable adding a deduplication id (hash of the log record). Defaults to True.
        dedup_keys (Optional[List]): Keys in the data to use for generation of deduplication id. Defaults to all keys.
        retry_count (int): Number of retries for sending logs. Defaults to config.DEFAULT_RETRY_COUNT.
        backoff_factor (float): Backoff factor for retries. Defaults to config.DEFAULT_BACKOFF_FACTOR.
        catch_all (bool): Flag to catch uncaught exceptions. Defaults to True.
        dedup_id_key (Optional[str]): Key for deduplication ID (no longer supported). Defaults to None.
        use_fallback (bool): Flag to use fallback host. Defaults to True.
        fallback_host (Optional[str]): Fallback host. Defaults to `host` prefixed by 'fallback.'.
        lvl_frame_info (int): Logging level to include frame information (no longer supported). Defaults to None.
        env_interval (int): Interval in seconds to send environment information. Defaults to config.DEFAULT_ENV_INTERVAL.
        internal (bool): attach an WatchtowerInternalHandler instead of a WatchtowerHandler, for logging directly to Splunk, bypassing the queue.

    Returns:
        logging.Logger: Configured Watchtower logger.
    """
    
    # issue warnings when arguments are specified that are no longer supported.
    if not path is None:
        warnings.warn('Logging to a file by specifying `path` is no longer supported directly by Watchtower, you can add your own file handler though.', DeprecationWarning)
    if not dedup_id_key is None:
        warnings.warn('Manually specifying the `dedup_id_key` is no longer supported', DeprecationWarning)
    if not lvl_frame_info is None:
        warnings.warn('The logging level for which frame information is send (`lvl_frame_info`) can no longer be specified', DeprecationWarning)
    if not debug is None:
        warnings.warn('Debug mode for the handler is no longer supported', DeprecationWarning)

    # add logging levels within the scope of the getLogger function
    # START and DONE are meant for scheduled functions that we want to monitor and detect if they ran at all (START) 
    # and finished correctly (DONE).
    logging.addLevelName(utils.logLevels.DONE, 'DONE')
    logging.addLevelName(utils.logLevels.START, 'START')

    # get the currently configured logger class
    initial_logging_class = logging.getLoggerClass()
    try:
        # temporarily change the logger class to WatchtowerLogger
        logging.setLoggerClass(klass=WatchtowerLogger)
        # instantiate a Watchtower logger
        name = utils.build_logger_name(name)
        logger = logging.getLogger(name)
    finally:
        # restore the initial logger class
        logging.setLoggerClass(klass=initial_logging_class)

    logger.setLevel(level)

    logger.init_default_data = default_data
    if default_data:
        logger.setDefaultData(data=default_data)

    logger.beam_id = beam_id
    logger.dev = dev
    logger.env = utils.get_environment() # environment information include Python version and installed packages
    logger.env_interval = env_interval # interval to send environment information (in seconds)
    logger.use_threading = use_threading

    # add host for use in send_alert function
    logger.host = host

    logger.setExecutionId(execution_id=execution_id)

    # configure sending to Watchtower if necessary
    if send:

        # Only allow secure protocol (https) in production, print a warning in development mode
        if protocol == 'http':
            if dev:
                warnings.warn('You are using an unsecure protocol (http). This will raise an error in production!', utils.ProtocolWarning)
            else:
                raise ValueError('Only secure protocol (https) is allowed in production')

        if use_threading and not utils.get_cf_name() is None:
            warnings.warn('You are using a Google Cloud Function but have threading enabled. This may not work as intended.', utils.UsageWarning)

        # Ensure no duplicate handlers are added
        if not logger.handlers or not any(isinstance(handler, (WatchtowerHandler, QueueHandler, WatchtowerInternalHandler)) for handler in logger.handlers):

            if not internal:
                # Set up the Watchtower handler to send logs to the specified endpoint
                watchtower_handler = WatchtowerHandler(beam_id=beam_id,
                                                       host=host,
                                                       token=token,
                                                       protocol=protocol,
                                                       retry_count=retry_count,
                                                       backoff_factor=backoff_factor,
                                                       use_fallback=use_fallback,
                                                       dedup=dedup,
                                                       dedup_keys=dedup_keys,
                                                       fallback_host=fallback_host,
                                                       dev=dev)
            
            else:
                # Set up the Watchtower internal handler to send logs to the specified splunk endpoint
                watchtower_handler = WatchtowerInternalHandler(host=host,
                                                               token=token,
                                                               protocol=protocol,
                                                               retry_count=retry_count,
                                                               backoff_factor=backoff_factor,
                                                               dev=dev)
            
            # We do not set level here with watchtower_handler.setLevel(level=level)
            # because we want the loglevel to be controllable with setLevel on the logger

            if not use_threading:

                # Add the handler directly if threading is disabled.
                logger.addHandler(watchtower_handler)
                   
            else:

                # Use a queue for asynchronous logging.
                log_queue = queue.Queue(-1)  # -1 means unlimited queue size
                queue_handler = QueueHandler(log_queue)
                logger.addHandler(queue_handler)
                
                # Start a queue listener to process logs in a separate thread.
                listener = CustomQueueListener(log_queue, watchtower_handler)
                listener.start()

                # Attach the listener to the logger
                logger.listener = listener

                # Register the listener to be shut down gracefully on exit.
                atexit.register(logger.shutdown)

    if console:

        # Add a console handler for outputting logs to the console, if one is not present yet.
        if not logger.handlers or not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):

            console_handler = logging.StreamHandler()
            # We do not set level here with console_handler.setLevel(level=level)
            # because we want the loglevel to be controllable with setLevel on the logger

            # Add a custom formatter to include additional log metadata.
            formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s - %(wt_extra_data)s')
            console_handler.setFormatter(formatter)

            logger.addHandler(console_handler)

    if catch_all:
        
        # Attach a global exception hook to the logger to catch uncaught exceptions.
        utils.attach_watchtower_exception_hook(logger)       

    return logger