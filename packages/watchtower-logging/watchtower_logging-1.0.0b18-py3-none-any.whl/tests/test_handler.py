import pytest
from unittest.mock import patch, MagicMock
from logging import LogRecord
from queue import Queue
from threading import Thread
import requests
import hashlib
import json

# Mock the required modules and variables
import sys
import types

version = types.ModuleType('version')
version.__version__ = '1.0.0'

sys.modules['watchtower_logging.version'] = version

# Now import the classes
from watchtower_logging.handlers import WatchtowerHandler, CustomQueueListener


def test_watchtower_handler_initialization():
    handler = WatchtowerHandler(
        beam_id='test_beam',
        host='example.com',
        token='test_token',
        protocol='https',
        retry_count=5,
        backoff_factor=0.2,
        use_fallback=True,
        fallback_host='fallback.example.com',
        http_timeout=10,
        dedup=True,
        dedup_keys=None
    )
    assert handler.beam_id == 'test_beam'
    assert handler.host == 'example.com'
    assert handler.token == 'test_token'
    assert handler.protocol == 'https'
    assert handler.retry_count == 5
    assert handler.backoff_factor == 0.2
    assert handler.use_fallback is True
    assert handler.fallback_host == 'fallback.example.com'
    assert handler.http_timeout == 10
    assert handler.dedup is True
    assert handler.dedup_keys is None

def test_format_time():
    handler = WatchtowerHandler(beam_id='test_beam', host='example.com')
    record = LogRecord(
        name='test_logger',
        level=20,
        pathname='test_path',
        lineno=10,
        msg='Test message',
        args=(),
        exc_info=None
    )
    record.created = 1609459200.123  # 2021-01-01 00:00:00.123 UTC
    record.msecs = 123
    formatted_time = handler.formatTime(record)
    assert formatted_time == '2021-01-01 00:00:00+0000,123'


def test_build_frame_info():
    handler = WatchtowerHandler(beam_id='test_beam', host='example.com')
    record = LogRecord(
        name='test_logger',
        level=20,
        pathname='/path/to/file.py',
        lineno=42,
        msg='Test message',
        args=(),
        exc_info=None
    )
    record.funcName = 'test_function'
    frame_info = handler.build_frame_info(record)
    assert frame_info == {
        'filename': '/path/to/file.py',
        'lineno': 42,
        'function': 'test_function'
    }


def test_generate_dedup_id():
    handler = WatchtowerHandler(beam_id='test_beam', host='example.com')
    handler.dedup_keys = None  # Since dedup_keys is not defined in __init__
    payload = {
        'message': 'Test message',
        'data': {
            'key1': 'value1',
            'key2': 'value2'
        }
    }
    dedup_id = handler.generate_dedup_id(payload)
    expected_dedup_id = hashlib.md5(json.dumps(
        payload, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
    assert dedup_id == expected_dedup_id


def test_build_payload():
    handler = WatchtowerHandler(beam_id='test_beam', host='example.com')
    record = LogRecord(
        name='test_logger',
        level=20,
        pathname='/path/to/file.py',
        lineno=42,
        msg='Test message',
        args=(),
        exc_info=None
    )
    record.funcName = 'test_function'
    record.created = 1609459200.123
    record.dev = 'dev_value'
    record.taskName = 'test_task'
    record.execution_id = 'exec123'
    record.env = 'test_env'
    record.data = {'extra_key': 'extra_value'}

    payload = handler.build_payload(record)
    assert payload['asctime'] == '2021-01-01T00:00:00.123000+0000'
    assert payload['name'] == 'test_logger'
    assert payload['levelname'] == 'INFO'
    assert payload['message'] == 'Test message'
    assert payload['dev'] == 'dev_value'
    assert payload['taskName'] == 'test_task'
    assert payload['execution_id'] == 'exec123'
    assert payload['beam_id'] == 'test_beam'
    assert payload['frame__'] == {
        'filename': '/path/to/file.py',
        'lineno': 42,
        'function': 'test_function'
    }
    assert payload['env__'] == 'test_env'
    assert payload['data']['extra_key'] == 'extra_value'
    assert 'dedup_id' in payload


def test_build_params():
    handler = WatchtowerHandler(beam_id='test_beam', host='example.com')
    record = LogRecord(
        name='test_logger',
        level=30,
        pathname='/path/to/file.py',
        lineno=50,
        msg='Another test message',
        args=(),
        exc_info=None
    )
    record.levelname = 'WARNING'
    record.execution_id = 'exec456'
    record.dedup_id = 'dedup123'
    record.asctime = '2021-01-02T00:00:00.123000+0000'

    params = handler.build_params(record)
    assert params == {
        'lvl': 'WARNING',
        'exec_id': 'exec456',
        'dedup': 'dedup123',
        't': '2021-01-02T00:00:00.123000+0000'
    }


@patch.object(WatchtowerHandler, 'send_log')
def test_emit(mock_send_log):
    handler = WatchtowerHandler(beam_id='test_beam', host='example.com')
    record = LogRecord(
        name='test_logger',
        level=20,
        pathname='/path/to/file.py',
        lineno=42,
        msg='Test message',
        args=(),
        exc_info=None
    )
    record.funcName = 'test_function'
    record.created = 1609459200.123
    record.dev = 'dev_value'
    record.taskName = 'test_task'
    record.execution_id = 'exec123'
    record.env = 'test_env'
    record.data = {'extra_key': 'extra_value'}
    handler.handle(record)
    mock_send_log.assert_called_once_with(payload=record.payload, params=record.params)


@patch('requests.Session.post')
def test_send_log_success(mock_post):
    handler = WatchtowerHandler(beam_id='test_beam', host='example.com', token='test_token')
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    payload = {'key': 'value'}
    params = {'param_key': 'param_value'}

    handler.send_log(payload, params)

    mock_post.assert_called_with(
        handler.url,
        json=payload,
        headers={
            'User-Agent': handler.user_agent,
            'Authorization': 'Token test_token'
        },
        params=params,
        timeout=handler.http_timeout
    )
    mock_response.raise_for_status.assert_called_once()


@patch('requests.Session.post')
def test_send_log_connection_error_with_fallback(mock_post):
    handler = WatchtowerHandler(beam_id='test_beam', host='example.com', use_fallback=True)
    mock_post.side_effect = requests.exceptions.ConnectionError

    payload = {'key': 'value'}
    params = {'param_key': 'param_value'}

    with patch.object(handler, '_send_fallback') as mock_send_fallback:
        handler.send_log(payload, params)
        mock_send_fallback.assert_called_once_with(payload, {'User-Agent': handler.user_agent})


@patch('requests.Session.post')
def test_send_log_http_error_with_fallback(mock_post):
    handler = WatchtowerHandler(beam_id='test_beam', host='example.com', use_fallback=True)
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    payload = {'key': 'value'}
    params = {'param_key': 'param_value'}

    with patch.object(handler, '_send_fallback') as mock_send_fallback:
        handler.send_log(payload, params)
        mock_send_fallback.assert_called_once_with(payload, {'User-Agent': handler.user_agent})


@patch('requests.Session.post')
def test_send_fallback_success(mock_post):
    handler = WatchtowerHandler(
        beam_id='test_beam',
        host='example.com',
        token='test_token',
        fallback_host='fallback.example.com'
    )
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    payload = {'key': 'value'}
    headers = {'User-Agent': handler.user_agent, 'Authorization': 'Token test_token'}

    handler._send_fallback(payload, headers)

    mock_post.assert_called_with(
        handler.fallback_url,
        json=payload,
        headers=headers,
        timeout=handler.http_timeout
    )
    mock_response.raise_for_status.assert_called_once()


def test_user_agent():
    handler = WatchtowerHandler(beam_id='test_beam', host='example.com')
    assert handler.user_agent == 'watchtower-logging-python/1.0.0'


def test_url():
    handler = WatchtowerHandler(beam_id='test_beam', host='example.com')
    assert handler.url == 'https://example.com/api/beams/test_beam'


def test_fallback_url():
    handler = WatchtowerHandler(
        beam_id='test_beam',
        host='example.com',
        fallback_host='fallback.example.com'
    )
    assert handler.fallback_url == 'https://fallback.example.com/api/beams/test_beam'


def test_custom_queue_listener_stop():
    handler = MagicMock()
    queue = Queue()
    listener = CustomQueueListener(queue, handler)
    listener._thread = Thread(target=lambda: None)
    listener._thread.start()
    listener.stop()
    assert listener._thread is None


def test_custom_queue_listener_stop_multiple_times():
    handler = MagicMock()
    queue = Queue()
    listener = CustomQueueListener(queue, handler)
    listener._thread = None
    listener.stop()  # Should not raise exception
    listener.stop()  # Should not raise exception