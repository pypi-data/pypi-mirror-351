import logging
import sys
import time
import traceback
import warnings
import string
from typing import Optional, Any, Dict, Callable

from watchtower_logging import config
from watchtower_logging import utils

class WatchtowerLogger(logging.Logger):

    def build_extra_object(self,
                           level: int,
                           data: Optional[dict] = None,
                           extra: Optional[dict] = None) -> Dict:
        
        """
        Method to build the data dictionary to send with logging events.

        Parameters:
            - level: Logging level (e.g., DEBUG, INFO, ERROR), to determine if traceback should be added to the data
            - data: Optional dictionary containing custom data for the log.
            - extra: Optional dictionary of additional parameters for the log.

        Returns:
            A merged dictionary of `data` and `extra`.
        """

        data = data or {}
        extra = extra or {}

        # Merge with default data if available, skip keys that are already in `extra`
        if hasattr(self, '_default_data') and isinstance(self._default_data, dict):
            data = {**{k: v for k, v in self._default_data.items() if k not in extra}, **data}

        # Add traceback if error level or higher and no traceback already present
        if level >= utils.logLevels.ERROR and 'traceback' not in data:
            exc_info = sys.exc_info()[2]
            if exc_info:
                data['traceback'] = traceback.format_exc() 
        
        # Raise an error if "data" key already exists in `extra`
        if data:
            if 'data' in extra:
                raise ValueError('Duplicate "data" key. Please merge the data you are passing with the entry in "extra".')
            extra['data'] = data       

        return extra

    def logaction(self,
                  level: int,
                  msg: str, 
                  *args: Any, 
                  data: Optional[dict]=None, 
                  **kwargs: Any) -> None:

        """
        Logs a message after building an extra object from `data` and `extra`.
        """

        if not self.isEnabledFor(level):

            return

        extra = self.build_extra_object(level=level, data=data, extra=kwargs.pop('extra', None))

        self.log(level, msg, *args, extra=extra, stacklevel=3, **kwargs)

    def makeRecord(self,
                   *args,
                   **kwargs) -> logging.LogRecord:
        
        """
        Overrides makeRecord to add custom attributes (dev, execution_id, env).

        Returns:
            A logging.LogRecord instance with custom fields.
        """

        rv = super(WatchtowerLogger, self).makeRecord(*args, **kwargs)
        rv.dev = self.dev
        rv.execution_id = self._execution_id
        rv.wt_extra_data = args[8]
        
        # Include environment details at a predefined interval
        if not hasattr(self, 'env_send_time') or time.time() - self.env_send_time > self.env_interval:
            rv.env = self.env
            self.env_send_time = time.time()

        return rv

    def done(self, 
             msg: str, 
             *args: Any,    
             data: Optional[dict]=None, 
             **kwargs: Any) -> None:
        
        """
        Logs a "DONE" level message.
        """

        self.logaction(msg=msg, level=utils.logLevels.DONE, *args, data=data, **kwargs)

    def start(self, 
              msg: str, 
              *args: Any, 
              data: Optional[dict]=None, 
              **kwargs: Any) -> None:
        
        """
        Logs a "START" level message.
        """

        self.logaction(msg=msg, level=utils.logLevels.START, *args, data=data, **kwargs)

    def debug(self, 
             msg: str, 
             *args: Any, 
             data: Optional[dict]=None, 
             **kwargs: Any) -> None:
        
        """
        Logs a "DEBUG" level message.
        """

        self.logaction(msg=msg, level=utils.logLevels.DEBUG, *args, data=data, **kwargs)

    def info(self, 
             msg: str, 
             *args: Any, 
             data: Optional[dict]=None, 
             **kwargs: Any) -> None:

        """
        Logs a "INFO" level message.
        """
        
        self.logaction(msg=msg, level=utils.logLevels.INFO, *args, data=data, **kwargs)

    def warning(self, 
                msg: str, 
                *args: Any, 
                data: Optional[dict]=None, 
                **kwargs: Any) -> None:
        
        """
        Logs a "WARNING" level message.
        """

        self.logaction(msg=msg, level=utils.logLevels.WARNING, *args, data=data, **kwargs)

    def error(self, 
              msg: str, 
              *args: Any, 
              data: Optional[dict]=None, 
              **kwargs: Any) -> None:

        """
        Logs a "ERROR" level message.
        """

        self.logaction(msg=msg, level=utils.logLevels.ERROR, *args, data=data, **kwargs)

    def critical(self, 
                 msg: str, 
                 *args: Any, 
                 data: Optional[dict]=None, 
                 **kwargs: Any) -> None:
        
        """
        Logs a "CRITICAL" level message.
        """

        self.logaction(msg=msg, level=utils.logLevels.CRITICAL, *args, data=data, **kwargs)

    def setExecutionId(self, 
                       execution_id: Optional[str]=None) -> None:
        
        """
        Sets the unique execution ID for the logger, generates a random one if None is given.
        """

        if execution_id is None:
            self._execution_id = ''.join(utils.random_choices(string.ascii_lowercase + string.digits, k=config.EXECUTION_ID_LENGTH))
        else:
            self._execution_id = execution_id

    def setDefaultData(self, 
                    data: dict, 
                    overwrite: bool=False) -> None:
        
        """
        Sets default data for all log messages.
        """

        if not isinstance(data, dict):
            raise TypeError('Default data needs to be a dictionary')
        if not overwrite and hasattr(self, '_default_data') and isinstance(self._default_data, dict):
            self._default_data = {**self._default_data, **data}
        else:
            self._default_data = data

    def setReturnWhenException(self, 
                               return_object: Optional[Any]=None) -> None:

        """
        Sets a return object. This object is returned by monitor_func
        when an uncaught exceptions occurs during execution.
        """

        self.return_when_exception = return_object

    def monitor_func(self,
                     *args,
                     **kwargs) -> Callable:
        
        """
        Wraps a function with monitoring capabilities.
        See utils.monitor_func for details

        Example Usage:

            @logger.monitor_func()
            def my_function():
                pass # do stuff that needs monitoring

        """

        return utils.monitor_func(logger=self, *args, **kwargs)

    def trigger_incident(self,
                         *args,
                         level: str = 'alert',
                         **kwargs) -> None:
        
        """
        Convenience method to trigger an alert incident directly. Should be used when an event occurs
        that warrants an incident immediately. Make sure that this does not get called too often.
        If more errors should together trigger an incident, consider sending logging messages and
        configure an alert in Watchtower.        
        """

        return utils.send_alert(self, *args, level=level, **kwargs)

    def send_alert(self,
                   *args,
                   **kwargs) -> None:

        """
        Old method, will be replaced by trigger_incident in the future      
        """
        
        warnings.warn('This method will be replaced by `trigger_incident` in the future, which has the same signature. Consider using that one instead')

        return self.trigger_incident(*args, **kwargs)
    
    def shutdown(self, timeout=None):
        
        """
        Stops the logger's listener thread, if applicable.
        """

        if hasattr(self, 'listener') and self.listener:
            try:
                self.listener.stop(timeout=timeout)
            except KeyboardInterrupt as e:
                print("KeyboardInterrupt received. Force quitting the listener thread.")
                # Allow the main thread to exit without waiting further



    
        

        

        