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
from watchtower_logging.handlers import WatchtowerInternalHandler


def test_watchtower_handler_initialization():
    handler = WatchtowerInternalHandler(
        host='example.com',
        token='test_token',
        protocol='https',
        retry_count=5,
        backoff_factor=0.2,
        http_timeout=10
    )
    assert handler.host == 'example.com'
    assert handler.token == 'test_token'
    assert handler.protocol == 'https'
    assert handler.retry_count == 5
    assert handler.backoff_factor == 0.2
    assert handler.fallback_host == 'fallback.example.com'
    assert handler.http_timeout == 10

def test_format_time():
    handler = WatchtowerInternalHandler(host='example.com', token='test_token')
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
    handler = WatchtowerInternalHandler(host='example.com', token='test_token')
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

def test_build_payload():
    handler = WatchtowerInternalHandler(host='example.com', token='test_token')
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
    assert payload['beam_id'] == '_internal'
    assert payload['frame__'] == {
        'filename': '/path/to/file.py',
        'lineno': 42,
        'function': 'test_function'
    }
    assert payload['env__'] == 'test_env'
    assert payload['data']['extra_key'] == 'extra_value'
    assert 'dedup_id' not in payload


def test_build_params():
    handler = WatchtowerInternalHandler(host='example.com', token='test_token')
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
    record.asctime = '2021-01-02T00:00:00.123000+0000'

    params = handler.build_params(record)
    assert params == {
        'lvl': 'WARNING',
        'exec_id': 'exec456',
        't': '2021-01-02T00:00:00.123000+0000'
    }

@patch.object(WatchtowerInternalHandler, 'send_log')
def test_emit(mock_send_log):
    handler = WatchtowerInternalHandler(host='example.com', token='test_token')
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

def test_meta():

    handler = WatchtowerInternalHandler(host='example.com', index='test_index', token='test_token')
    meta = handler.default_meta

    assert meta == {
        'index': 'test_index',
        'source': 'watchtower_internal_logging',
        'sourcetype': '_json',
        'host': 'internal' }

@patch('requests.Session.post')
def test_send_log_success(mock_post):
    handler = WatchtowerInternalHandler(host='example.com', token='test_token')
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    payload = {'key': 'value'}
    params = {'param_key': 'param_value'}

    handler.send_log(payload, params)

    event = {**handler.default_meta,
             'event': payload}

    mock_post.assert_called_with(
        handler.url,
        json=event,
        headers={
            'User-Agent': handler.user_agent,
            'Authorization': 'Splunk test_token'
        },
        timeout=handler.http_timeout
    )
    mock_response.raise_for_status.assert_called_once()


def test_user_agent():
    handler = WatchtowerInternalHandler(host='example.com', token='test_token')
    assert handler.user_agent == 'watchtower-logging-python/1.0.0/internal'


def test_url():
    handler = WatchtowerInternalHandler(host='example.com', token='test_token')
    assert handler.url == 'https://example.com/services/collector/event'