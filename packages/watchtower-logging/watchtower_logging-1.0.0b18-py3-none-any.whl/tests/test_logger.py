import pytest
from unittest.mock import patch, MagicMock
import sys
import types
import logging
import time
import warnings



utils = types.ModuleType('utils')

# Define custom log levels
class LogLevels:
    ERROR = logging.ERROR
    DONE = 25    # Custom level between INFO (20) and WARNING (30)
    START = 15   # Custom level between DEBUG (10) and INFO (20)
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    CRITICAL = logging.CRITICAL

utils.logLevels = LogLevels()

# Mock random_choices function
def mock_random_choices(seq, k):
    return ['a'] * k  # Return a list of 'a's of length k

utils.random_choices = mock_random_choices

# Mock monitor_func and send_alert functions
def mock_monitor_func(logger, *args, **kwargs):
    def decorator(func):
        def wrapper(*a, **kw):
            return func(*a, **kw)
        return wrapper
    return decorator

utils.monitor_func = mock_monitor_func

def mock_send_alert(logger, *args, **kwargs):
    pass

utils.send_alert = mock_send_alert

# Inject mock modules into sys.modules
sys.modules['watchtower_logging.utils'] = utils

# Now import the class
from watchtower_logging.loggers import WatchtowerLogger


def test_build_extra_object():
    logger = WatchtowerLogger('test_logger')

    # Test merging data and extra
    level = utils.logLevels.INFO
    data = {'key1': 'value1'}
    extra = {'key2': 'value2'}
    result = logger.build_extra_object(level=level, data=data, extra=extra)
    expected = {
        'key2': 'value2',
        'data': {'key1': 'value1'}
    }
    assert result == expected

    # Test adding traceback when level >= ERROR
    level = utils.logLevels.ERROR
    try:
        raise Exception('Test exception')
    except Exception:
        result = logger.build_extra_object(level=level)
        assert 'traceback' in result['data']
        assert isinstance(result['data']['traceback'], str)

    # Test raising ValueError when 'data' key is in extra
    with pytest.raises(ValueError):
        logger.build_extra_object(level=level, data=data, extra={'data': 'should not be here'})

    # Test merging with default data
    logger._default_data = {'default_key': 'default_value'}
    result = logger.build_extra_object(level=level, data={'key1': 'value1'}, extra={'key2': 'value2'})
    expected = {
        'key2': 'value2',
        'data': {'default_key': 'default_value', 'key1': 'value1'}
    }
    assert result == expected

     # Test merging with default data. Should be overwritten by keys in extra
    logger._default_data = {'key2': 'value3'}
    result = logger.build_extra_object(level=level, data={'key1': 'value1'}, extra={'key2': 'value2'})
    expected = {
        'key2': 'value2',
        'data': {'key1': 'value1'}
    }
    assert result == expected


def test_logaction():
    logger = WatchtowerLogger('test_logger')
    logger.isEnabledFor = MagicMock(return_value=True)
    logger.log = MagicMock()
    level = utils.logLevels.INFO
    msg = 'Test message'
    data = {'key1': 'value1'}
    extra = {'key2': 'value2'}
    kwargs = {'extra': extra}

    with patch.object(logger, 'build_extra_object', return_value={'key2': 'value2', 'data': data}):
        logger.logaction(level=level, msg=msg, data=data, **kwargs)
        logger.log.assert_called_with(level, msg, extra={'key2': 'value2', 'data': data}, stacklevel=3)

    # Test early return if not enabled for level
    logger.isEnabledFor = MagicMock(return_value=False)
    logger.log.reset_mock()
    logger.logaction(level=level, msg=msg)
    logger.log.assert_not_called()


def test_makeRecord():
    logger = WatchtowerLogger('test_logger')
    logger.dev = 'dev_value'
    logger.env = {'lng': 'Python'}
    logger._execution_id = 'exec123'
    logger.env_interval = 10
    args = ('name', utils.logLevels.INFO, 'pathname', 1, 'msg', [], None, {}, {})
    kwargs = {}
    record = logger.makeRecord(*args, **kwargs)
    assert record.dev == 'dev_value'
    assert record.execution_id == 'exec123'
    assert record.wt_extra_data == args[8]
    assert record.env == {'lng': 'Python'}

    # Test setting env at predefined interval
    with patch('time.time', return_value=1000):
        logger.env_send_time = 900
        record = logger.makeRecord(*args, **kwargs)
        assert record.env == {'lng': 'Python'}
        assert logger.env_send_time == 1000

    with patch('time.time', return_value=1000):
        logger.env_send_time = 999
        record = logger.makeRecord(*args, **kwargs)
        assert not hasattr(record, 'env')


def test_logging_methods():
    logger = WatchtowerLogger('test_logger')
    with patch.object(logger, 'logaction') as mock_logaction:
        logger.done('Done message', data={'key': 'value'})
        mock_logaction.assert_called_with(level=utils.logLevels.DONE, msg='Done message', data={'key': 'value'})

        logger.start('Start message')
        mock_logaction.assert_called_with(level=utils.logLevels.START, msg='Start message', data=None)

        logger.debug('Debug message')
        mock_logaction.assert_called_with(level=utils.logLevels.DEBUG, msg='Debug message', data=None)

        logger.info('Info message')
        mock_logaction.assert_called_with(level=utils.logLevels.INFO, msg='Info message', data=None)

        logger.warning('Warning message')
        mock_logaction.assert_called_with(level=utils.logLevels.WARNING, msg='Warning message', data=None)

        logger.error('Error message')
        mock_logaction.assert_called_with(level=utils.logLevels.ERROR, msg='Error message', data=None)

        logger.critical('Critical message')
        mock_logaction.assert_called_with(level=utils.logLevels.CRITICAL, msg='Critical message', data=None)


def test_setExecutionId():
    logger = WatchtowerLogger('test_logger')
    logger.setExecutionId('custom_id')
    assert logger._execution_id == 'custom_id'

    # Test generating random execution_id
    with patch('watchtower_logging.utils.random_choices', return_value=['a', 'b', 'c']):
        logger.setExecutionId()
        assert logger._execution_id == 'abc'


def test_setDefaultData():
    logger = WatchtowerLogger('test_logger')
    data = {'key1': 'value1'}
    logger.setDefaultData(data)
    assert logger._default_data == data

    # Test TypeError when data is not a dict
    with pytest.raises(TypeError):
        logger.setDefaultData(['not', 'a', 'dict'])

    # Test merging data when overwrite is False
    logger.setDefaultData({'key2': 'value2'})
    assert logger._default_data == {'key1': 'value1', 'key2': 'value2'}

    # Test overwriting data
    logger.setDefaultData({'key3': 'value3'}, overwrite=True)
    assert logger._default_data == {'key3': 'value3'}


def test_setReturnWhenException():
    logger = WatchtowerLogger('test_logger')
    logger.setReturnWhenException('return_value')
    assert logger.return_when_exception == 'return_value'


def test_monitor_func():
    logger = WatchtowerLogger('test_logger')
    with patch('watchtower_logging.utils.monitor_func') as mock_monitor_func:
        mock_monitor_func.return_value = 'decorated_func'
        result = logger.monitor_func()
        assert result == 'decorated_func'
        mock_monitor_func.assert_called_with(logger=logger)


def test_trigger_incident():
    logger = WatchtowerLogger('test_logger')
    with patch('watchtower_logging.utils.send_alert') as mock_send_alert:
        logger.trigger_incident('arg1', key='value')
        mock_send_alert.assert_called_with(logger, 'arg1', level='alert', key='value')


def test_send_alert():
    logger = WatchtowerLogger('test_logger')
    with patch.object(logger, 'trigger_incident') as mock_trigger_incident:
        with warnings.catch_warnings(record=True) as w:
            logger.send_alert('arg1', key='value')
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert 'This method will be replaced by `trigger_incident` in the future' in str(w[-1].message)
            mock_trigger_incident.assert_called_with('arg1', key='value')


def test_shutdown():
    logger = WatchtowerLogger('test_logger')
    listener_mock = MagicMock()
    logger.listener = listener_mock
    logger.shutdown()
    listener_mock.stop.assert_called_once_with(timeout=None)

    # Test handling KeyboardInterrupt
    listener_mock.stop.side_effect = KeyboardInterrupt
    with patch('builtins.print') as mock_print:
        logger.shutdown()
        mock_print.assert_called_with("KeyboardInterrupt received. Force quitting the listener thread.")