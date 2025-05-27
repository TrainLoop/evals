"""
Unit tests for the logger module.
"""
import os
import logging
from unittest.mock import patch, MagicMock

from trainloop_llm_logging.logger import create_logger, _configure_root_once


class TestLogger:
    """Test the logger module."""

    def test_configure_root_once_sets_logging_config(self):
        """Test that _configure_root_once configures root logger."""
        # Reset the _done flag if it exists
        if hasattr(_configure_root_once, '_done'):
            delattr(_configure_root_once, '_done')
        
        with patch('logging.basicConfig') as mock_basic_config:
            _configure_root_once()
            
            # Should call basicConfig with correct parameters
            mock_basic_config.assert_called_once()
            call_args = mock_basic_config.call_args
            
            assert call_args[1]['level'] == logging.WARN  # Default level
            assert '[%(levelname)s]' in call_args[1]['format']
            assert '[%(asctime)s]' in call_args[1]['format']
            assert '[%(name)s]' in call_args[1]['format']
            assert '%(message)s' in call_args[1]['format']
            assert call_args[1]['force'] is True

    def test_configure_root_once_only_runs_once(self):
        """Test that _configure_root_once only runs once."""
        # Reset the _done flag
        if hasattr(_configure_root_once, '_done'):
            delattr(_configure_root_once, '_done')
        
        with patch('logging.basicConfig') as mock_basic_config:
            # First call
            _configure_root_once()
            assert mock_basic_config.call_count == 1
            
            # Second call should not reconfigure
            _configure_root_once()
            assert mock_basic_config.call_count == 1  # Still only 1

    @patch.dict(os.environ, {'TRAINLOOP_LOG_LEVEL': 'DEBUG'})
    def test_configure_root_once_respects_env_var(self):
        """Test that _configure_root_once respects TRAINLOOP_LOG_LEVEL."""
        # Reset the _done flag
        if hasattr(_configure_root_once, '_done'):
            delattr(_configure_root_once, '_done')
        
        with patch('logging.basicConfig') as mock_basic_config:
            _configure_root_once()
            
            # Should use DEBUG level from env var
            call_args = mock_basic_config.call_args
            assert call_args[1]['level'] == logging.DEBUG

    @patch.dict(os.environ, {'TRAINLOOP_LOG_LEVEL': 'INFO'})
    def test_configure_root_once_handles_info_level(self):
        """Test that _configure_root_once handles INFO level."""
        # Reset the _done flag
        if hasattr(_configure_root_once, '_done'):
            delattr(_configure_root_once, '_done')
        
        with patch('logging.basicConfig') as mock_basic_config:
            _configure_root_once()
            
            call_args = mock_basic_config.call_args
            assert call_args[1]['level'] == logging.INFO

    @patch.dict(os.environ, {'TRAINLOOP_LOG_LEVEL': 'ERROR'})
    def test_configure_root_once_handles_error_level(self):
        """Test that _configure_root_once handles ERROR level."""
        # Reset the _done flag
        if hasattr(_configure_root_once, '_done'):
            delattr(_configure_root_once, '_done')
        
        with patch('logging.basicConfig') as mock_basic_config:
            _configure_root_once()
            
            call_args = mock_basic_config.call_args
            assert call_args[1]['level'] == logging.ERROR

    @patch.dict(os.environ, {'TRAINLOOP_LOG_LEVEL': 'INVALID'})
    def test_configure_root_once_handles_invalid_level(self):
        """Test that _configure_root_once handles invalid log level."""
        # Reset the _done flag
        if hasattr(_configure_root_once, '_done'):
            delattr(_configure_root_once, '_done')
        
        with patch('logging.basicConfig') as mock_basic_config:
            _configure_root_once()
            
            # Should default to INFO for invalid levels
            call_args = mock_basic_config.call_args
            assert call_args[1]['level'] == logging.INFO

    @patch.dict(os.environ, {'TRAINLOOP_LOG_LEVEL': 'warn'})
    def test_configure_root_once_handles_lowercase_level(self):
        """Test that _configure_root_once handles lowercase log level."""
        # Reset the _done flag
        if hasattr(_configure_root_once, '_done'):
            delattr(_configure_root_once, '_done')
        
        with patch('logging.basicConfig') as mock_basic_config:
            _configure_root_once()
            
            # Should handle lowercase by converting to uppercase
            call_args = mock_basic_config.call_args
            assert call_args[1]['level'] == logging.WARN

    def test_create_logger_returns_named_logger(self):
        """Test that create_logger returns a properly named logger."""
        logger = create_logger("test-scope")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test-scope"

    def test_create_logger_calls_configure_root_once(self):
        """Test that create_logger ensures root is configured."""
        # Reset the _done flag
        if hasattr(_configure_root_once, '_done'):
            delattr(_configure_root_once, '_done')
        
        with patch('logging.basicConfig') as mock_basic_config:
            logger = create_logger("test-logger")
            
            # Should have configured root
            mock_basic_config.assert_called_once()
            
            # And return a logger
            assert isinstance(logger, logging.Logger)

    def test_multiple_create_logger_calls_share_root_config(self):
        """Test that multiple loggers share the same root configuration."""
        # Reset the _done flag
        if hasattr(_configure_root_once, '_done'):
            delattr(_configure_root_once, '_done')
        
        with patch('logging.basicConfig') as mock_basic_config:
            logger1 = create_logger("logger-1")
            logger2 = create_logger("logger-2")
            logger3 = create_logger("logger-3")
            
            # Root should only be configured once
            assert mock_basic_config.call_count == 1
            
            # All loggers should be different instances with different names
            assert logger1.name == "logger-1"
            assert logger2.name == "logger-2"
            assert logger3.name == "logger-3"
            assert logger1 is not logger2
            assert logger2 is not logger3

    def test_logger_inherits_root_handlers(self):
        """Test that created loggers inherit root logger configuration."""
        # This is more of an integration test but valuable to ensure
        # the loggers work as expected
        logger = create_logger("inheritance-test")
        
        # Logger should use root logger's handlers (propagate is True by default)
        assert logger.propagate is True
        
        # Should not have its own handlers (uses root's)
        assert len(logger.handlers) == 0

    @patch('logging.getLogger')
    def test_create_logger_uses_logging_getLogger(self, mock_get_logger):
        """Test that create_logger uses the standard logging.getLogger."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        result = create_logger("mock-test")
        
        mock_get_logger.assert_called_once_with("mock-test")
        assert result == mock_logger
