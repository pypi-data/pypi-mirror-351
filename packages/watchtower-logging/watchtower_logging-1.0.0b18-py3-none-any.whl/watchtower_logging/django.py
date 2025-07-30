import queue
from logging.handlers import QueueListener, QueueHandler
from watchtower_logging.handlers import WatchtowerHandler
import atexit

class WatchtowerQueueHandler(QueueHandler):

    """
    This is a Watchtower queue handler for use in Django.
    It also starts queue and a corresponding listener.
    Should be used in LOGGING definition in the Django settings. 
    Settings that can be used are:

        - WT_BEAM_ID (required)
        - WT_HOST (required)
        - WT_TOKEN (defaults to None)
        - WT_PROTOCOL (defaults to 'https')
        - WT_NUM_RETRY (defaults to 1)
        - WT_BACKOFF_FACTOR (defaults to 1)
        - WT_USE_FALLBACK (defaults to True)
        - WT_FALLBACK_HOST (defaults to None)
        - WT_DEDUP (defaults to True)
        - WT_DEDUP_KEYS (defaults to None)
        - WT_HTTP_TIMEOUT (defaults to 1.0)
        - WT_DEV (defaults to settings.DEBUG)

    # For example, you can add this to settings.py
        
        WT_BEAM_ID = 'your-beam-id'
        WT_HOST = 'your.watchtower.host'
        WT_TOKEN = 'your-beam-token'
        WT_HTTP_TIMEOUT = 0.5

        LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                'watchtower': {
                    'level': 'INFO',
                    'class': 'watchtower_logging.django.WatchtowerQueueHandler'
                },
            },
            'loggers': {
                '': {
                    'handlers': ['watchtower'],
                    'level': 'INFO',
                    'propagate': True,
                },
            },
        }

    """

    def __init__(self):
        
        # Use a queue for asynchronous logging.
        log_queue = self.init_queue()
        
        # Start a queue listener to process logs in a separate thread.
        watchtower_handler = self.init_watchtower_handler()
        listener = QueueListener(log_queue, watchtower_handler)
        
        # Start the listener and register it to be shut down gracefully on exit.
        listener.start()
        atexit.register(listener.stop)

        super().__init__(log_queue)

    def init_queue(self) -> queue.Queue:

        return queue.Queue(-1)

    def init_watchtower_handler(self) -> WatchtowerHandler:

        return WatchtowerHandler.for_django()