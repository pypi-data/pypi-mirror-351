import pytest
from unittest.mock import patch, MagicMock
import queue
import logging

from watchtower_logging.django import WatchtowerQueueHandler
from watchtower_logging.handlers import WatchtowerHandler


@pytest.fixture
def mock_django():

    """Fixture to mock Django settings without requiring Django installed."""
    mock_settings = MagicMock()
    mock_settings.WT_BEAM_ID = 'test-beam'
    mock_settings.WT_HOST = 'test.watchtower.host'
    mock_settings.WT_TOKEN = 'test-token'
    mock_settings.WT_PROTOCOL = 'https'
    mock_settings.DEBUG = False
    mock_settings.WT_DEV = False
    mock_settings.WT_NUM_RETRY = 2
    mock_settings.WT_BACKOFF_FACTOR = 2
    mock_settings.WT_USE_FALLBACK = True
    mock_settings.WT_FALLBACK_HOST = 'fallback.test.watchtower.host'
    mock_settings.WT_DEDUP = True
    mock_settings.WT_DEDUP_KEYS = ('x', 'y')
    mock_settings.WT_HTTP_TIMEOUT = 2.0

    mock_django = MagicMock()
    mock_django.conf.settings = mock_settings

    with patch.dict('sys.modules', {'django': mock_django, 'django.conf': mock_django.conf}):
        yield


def test_queue_handler_initialization(mock_django):
    """Test WatchtowerQueueHandler initializes correctly."""
    with patch('watchtower_logging.django.atexit') as mock_atexit:
        handler = WatchtowerQueueHandler()
        
        # Verify queue initialization
        assert isinstance(handler.queue, queue.Queue)
        assert handler.queue.maxsize == -1  # Unlimited queue size
        
        # Verify listener registration
        mock_atexit.register.assert_called_once()


def test_watchtower_handler_creation(mock_django):
    """Test WatchtowerHandler is created with correct Django settings."""
    handler = WatchtowerQueueHandler()
    wt_handler = handler.init_watchtower_handler()
    
    assert isinstance(wt_handler, WatchtowerHandler)
    assert wt_handler.beam_id == 'test-beam'
    assert wt_handler.host == 'test.watchtower.host'
    assert wt_handler.token == 'test-token'
    assert wt_handler.protocol == 'https'
    assert wt_handler.dev == False
    assert wt_handler.use_fallback == True
    assert wt_handler.fallback_host == 'fallback.test.watchtower.host'
    assert wt_handler.dedup == True
    assert wt_handler.dedup_keys == ('x', 'y')
    assert wt_handler.http_timeout == 2.0
    assert wt_handler.retry_count == 2
    assert wt_handler.backoff_factor == 2


@patch('watchtower_logging.django.QueueListener')
def test_queue_listener_behavior(mock_queue_listener, mock_django):
    """Test queue listener is started and handles messages correctly."""
    mock_listener = MagicMock()
    mock_queue_listener.return_value = mock_listener
    
    handler = WatchtowerQueueHandler()
    
    # Verify listener was started
    mock_listener.start.assert_called_once()
    
    # Test message handling
    test_record = logging.LogRecord(
        name='test_logger',
        level=logging.INFO,
        pathname='test.py',
        lineno=1,
        msg='Test message',
        args=(),
        exc_info=None
    )
    
    handler.emit(test_record)
    assert not handler.queue.empty()