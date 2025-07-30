import pytest
from unittest.mock import patch, MagicMock
import sys
import logging
import random

# Mock the required modules and variables
import types

# Mock version module
version = types.ModuleType('version')
version.__version__ = '1.0.0'
sys.modules['watchtower_logging.version'] = version

# Now import the code to test
from watchtower_logging.utils import (build_logger_name, 
                                      parse_requirements, 
                                      get_environment, 
                                      monitor_func, 
                                      send_alert, 
                                      random_choices, 
                                      attach_watchtower_exception_hook, 
                                      logLevels,
                                      ProtocolWarning)

from watchtower_logging import config

def test_logLevels():
    assert logLevels.DEBUG == logging.DEBUG
    assert logLevels.INFO == logging.INFO
    assert logLevels.START == config.START_LEVEL_NUM
    assert logLevels.DONE == config.DONE_LEVEL_NUM
    assert logLevels.WARNING == logging.WARNING
    assert logLevels.ERROR == logging.ERROR
    assert logLevels.CRITICAL == logging.CRITICAL

def test_build_logger_name_env_variables(monkeypatch):
    monkeypatch.setenv('K_SERVICE', 'service_logger')
    logger_name = build_logger_name(None)
    assert logger_name == 'service_logger'

def test_build_logger_name_function_name(monkeypatch):
    monkeypatch.delenv('K_SERVICE', raising=False)
    monkeypatch.setenv('FUNCTION_NAME', 'function_logger')
    logger_name = build_logger_name(None)
    assert logger_name == 'function_logger'

def test_build_logger_name_default(monkeypatch):
    monkeypatch.delenv('K_SERVICE', raising=False)
    monkeypatch.delenv('FUNCTION_NAME', raising=False)
    logger_name = build_logger_name(None)
    assert logger_name == config.DEFAULT_LOGGER_NAME

def test_build_logger_name_provided_name():
    logger_name = build_logger_name('provided_logger')
    assert logger_name == 'provided_logger'

def test_parse_requirements():
    input_str = """
    requests==2.25.1
    pytest>=6.0.0
    numpy
    """
    requirements = parse_requirements(input_str)
    assert requirements == [
        {'name': 'requests', 'version': '2.25.1'},
        {'name': 'pytest', 'version': '>=6.0.0'},
        {'name': 'numpy', 'version': ''}
    ]

@patch('platform.python_version')
@patch('subprocess.run')
def test_get_environment(mock_run, mock_platform):
    mock_run.return_value = MagicMock(stdout='requests==2.25.1\npytest>=6.0.0\nnumpy')
    mock_platform.return_value = '3.12.1'
    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = 'requests==2.25.1\nnumpy'
        env = get_environment()
        assert env['lng'] == 'Python'
        assert env['lng_version'] == '3.12.1'
        assert 'packages' in env
        assert env['packages'] == [
            {'name': 'requests', 'version': '2.25.1'},
            {'name': 'numpy', 'version': ''}
        ]
@patch('platform.python_version')
@patch('subprocess.run')
def test_get_environment_subprocess_exception(mock_run, mock_platform):
    mock_platform.return_value = '3.12.1'
    mock_run.side_effect = Exception('Subprocess error')
    env = get_environment()
    assert env == {'lng': 'Python', 'lng_version': '3.12.1'}

@patch('platform.python_version')
@patch('subprocess.run')
def test_get_environment_subprocess_exception(mock_run, mock_platform):
    mock_run.return_value = MagicMock(stdout='requests==2.25.1\npytest>=6.0.0\nnumpy')
    mock_platform.side_effect = Exception('Platform error error')
    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = 'requests==2.25.1\nnumpy'
        env = get_environment()
        assert env['lng'] == 'Python'
        assert 'lng_version' not in env
        assert 'packages' in env
        assert env['packages'] == [
            {'name': 'requests', 'version': '2.25.1'},
            {'name': 'numpy', 'version': ''}
        ]
def test_monitor_func():
    # Mock logger
    logger = MagicMock()
    logger.setExecutionId = MagicMock()
    logger.setDefaultData = MagicMock()
    logger.start = MagicMock()
    logger.done = MagicMock()
    logger.error = MagicMock()
    logger.critical = MagicMock()
    logger.host = 'example.com'

    # Decorated function
    @monitor_func(logger=logger, func_name='test_func', start_done=True)
    def test_function(x, y):
        return x + y

    result = test_function(2, 3)
    assert result == 5
    logger.setExecutionId.assert_called_once()
    logger.start.assert_called_once_with('Starting test_func')
    logger.done.assert_called_once_with('Done with test_func')
    logger.setDefaultData.assert_called()
    logger.error.assert_not_called()
    logger.critical.assert_not_called()

def test_monitor_func_exception():
    # Mock logger
    logger = MagicMock()
    logger.setExecutionId = MagicMock()
    logger.setDefaultData = MagicMock()
    logger.start = MagicMock()
    logger.done = MagicMock()
    logger.error = MagicMock()
    logger.critical = MagicMock()
    logger.host = 'example.com'

    # Decorated function that raises an exception
    @monitor_func(logger=logger, func_name='test_func', start_done=True, except_level='ERROR')
    def test_function():
        raise ValueError('Test exception')

    result = test_function()
    logger.setExecutionId.assert_called_once()
    logger.start.assert_called_once_with('Starting test_func')
    logger.done.assert_not_called()
    logger.error.assert_called()
    assert logger.error.call_args[0][0] == 'Test exception'
    logger.critical.assert_not_called()

def test_monitor_func_return_when_exception():
    # Mock logger
    logger = MagicMock()
    logger.setExecutionId = MagicMock()
    logger.setDefaultData = MagicMock()
    logger.start = MagicMock()
    logger.done = MagicMock()
    logger.error = MagicMock()
    logger.critical = MagicMock()
    logger.host = 'example.com'
    logger.return_when_exception = 'default_value'

    # Decorated function that raises an exception
    @monitor_func(logger=logger)
    def test_function():
        raise ValueError('Test exception')

    result = test_function()
    assert result == 'default_value'

def test_monitor_func_http_exception(monkeypatch):
    # Mock logger
    logger = MagicMock()
    logger.setExecutionId = MagicMock()
    logger.setDefaultData = MagicMock()
    logger.start = MagicMock()
    logger.done = MagicMock()
    logger.error = MagicMock()
    logger.critical = MagicMock()
    logger.host = 'example.com'
    del logger.return_when_exception  # Ensure it's not set

    # Set FUNCTION_SIGNATURE_TYPE to 'http'
    monkeypatch.setenv('FUNCTION_SIGNATURE_TYPE', 'http')

    # Decorated function that raises an exception
    @monitor_func(logger=logger)
    def test_function():
        raise ValueError('Test exception')

    result = test_function()
    assert result == ({'details': 'Server Error'}, 500)

def test_send_alert_success():
    # Mock logger
    logger = MagicMock()
    logger.host = 'example.com'

    # Mock requests
    with patch('requests.Session') as mock_session:
        mock_post = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.post.return_value = mock_response
        mock_session.return_value = mock_post

        send_alert(logger=logger,
                   alert_token='valid_token_12345',
                   name='Test Alert',
                   lead='Test Lead')

        mock_post.post.assert_called()
        args, kwargs = mock_post.post.call_args
        assert args[0] == 'https://alerts.example.com'
        assert 'json' in kwargs
        assert kwargs['headers']['Authorization'] == 'valid_token_12345'

def test_send_alert_failure():
    # Mock logger
    logger = MagicMock()
    logger.host = 'example.com'
    logger.critical = MagicMock()

    # Mock requests to raise exception
    with patch('requests.Session') as mock_session:
        mock_post = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception('HTTP Error')
        mock_post.post.return_value = mock_response
        mock_session.return_value = mock_post

        send_alert(logger=logger,
                   alert_token='valid_token_12345',
                   name='Test Alert',
                   lead='Test Lead')

        logger.critical.assert_called()
        args, kwargs = logger.critical.call_args
        assert 'Failed to send alert' in args[0]

def test_send_alert_invalid_alert_token():
    # Mock logger
    logger = MagicMock()
    logger.host = 'example.com'
    logger.critical = MagicMock()

    send_alert(logger=logger,
               alert_token='short',
               name='Test Alert',
               lead='Test Lead')

    logger.critical.assert_called()
    args, kwargs = logger.critical.call_args
    assert 'Failed to send alert' in args[0]
    assert 'Invalid alert token' in kwargs['data']['error']

def test_random_choices():
    population = ['a', 'b', 'c', 'd']
    weights = [0.1, 0.2, 0.3, 0.4]
    k = 5

    original_choices = random.choices
    del random.choices

    try:
        # Test custom implementation
        result = random_choices(population, weights=weights, k=k)
        assert len(result) == k
        for item in result:
            assert item in population
    finally:
        # Restore 'choices' to random
        random.choices = original_choices

def test_random_choices_python3():
    population = ['a', 'b', 'c', 'd']
    weights = [0.1, 0.2, 0.3, 0.4]
    k = 5

    with patch('random.choices', return_value=['a', 'b', 'c', 'd', 'a']):
        # Test built-in implementation
        result = random_choices(population, weights=weights, k=k)
        assert result == ['a', 'b', 'c', 'd', 'a']

def test_attach_watchtower_exception_hook():
    logger = MagicMock()
    logger.critical = MagicMock()

    # Save the original excepthook
    original_excepthook = sys.excepthook

    try:
        attach_watchtower_exception_hook(logger)

        # Simulate an exception
        try:
            raise ValueError('Test exception')
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            sys.excepthook(exc_type, exc_value, exc_traceback)

        logger.critical.assert_called()
        args, kwargs = logger.critical.call_args
        assert 'Uncaught Exception' in args[0]
        assert 'traceback' in kwargs['data']
    finally:
        # Restore the original excepthook
        sys.excepthook = original_excepthook

def test_attach_watchtower_exception_hook_keyboard_interrupt():
    logger = MagicMock()
    logger.critical = MagicMock()

    # Save the original excepthook
    original_excepthook = sys.excepthook

    try:
        attach_watchtower_exception_hook(logger)

        # Mock sys.__excepthook__
        sys.__excepthook__ = MagicMock()

        # Simulate a KeyboardInterrupt
        try:
            raise KeyboardInterrupt()
        except KeyboardInterrupt:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            sys.excepthook(exc_type, exc_value, exc_traceback)

        logger.critical.assert_not_called()
        sys.__excepthook__.assert_called()
    finally:
        # Restore the original excepthook
        sys.excepthook = original_excepthook

def test_protocol_warning():
    assert issubclass(ProtocolWarning, Warning)
