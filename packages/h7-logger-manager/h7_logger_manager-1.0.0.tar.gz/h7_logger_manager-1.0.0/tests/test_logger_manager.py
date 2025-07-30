import logging
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add the src directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from h7_logger_manager.logger_manager import LoggerManager
from pathlib import Path
import tempfile



class TestLoggerManager(unittest.TestCase):

    @patch('h7_logger_manager.logger_manager.RotatingFileHandler')
    @patch('h7_logger_manager.logger_manager.EnvManager')
    @patch('h7_logger_manager.logger_manager.find_project_root')
    @patch('h7_logger_manager.logger_manager.os.path.exists')
    @patch('h7_logger_manager.logger_manager.os.makedirs')
    def test_setup_logger(self, mock_makedirs, mock_exists, mock_find_logs, mock_env_manager, mock_rotating_handler):
        """Test that setup_logger creates and returns a logger"""
        with tempfile.TemporaryDirectory() as temp_logs_dir:
            mock_exists.return_value = True
            temp_path = Path(temp_logs_dir)
            mock_find_logs.return_value = temp_path
            mock_env_manager.get_required_env_var.return_value = "test_logger"
            mock_env_manager.get_optional_env_var.return_value = "false"
            mock_rotating_handler.return_value = unittest.mock.Mock()

            LoggerManager._loggers = {}

            logger = LoggerManager.setup_logger()

            self.assertIsInstance(logger, logging.Logger)
            self.assertEqual(logger.name, "test_logger")
            self.assertEqual(len(logger.handlers), 2)

            logger2 = LoggerManager.setup_logger()
            self.assertIs(logger2, logger)

    @patch("h7_logger_manager.logger_manager.RotatingFileHandler")
    @patch("h7_logger_manager.logger_manager.EnvManager")
    @patch("h7_logger_manager.logger_manager.find_project_root")
    @patch("h7_logger_manager.logger_manager.os.path.exists")
    @patch("h7_logger_manager.logger_manager.os.makedirs")
    def test_setup_logger_with_custom_name(
        self, mock_makedirs, mock_exists, mock_find_logs, mock_env_manager, mock_rotating_handler
    ):
        """Test that setup_logger works with a custom logger name"""
        with tempfile.TemporaryDirectory() as temp_logs_dir:
            mock_exists.return_value = False
            temp_path = Path(temp_logs_dir)
            mock_find_logs.return_value = temp_path
            mock_env_manager.get_optional_env_var.return_value = "true"
            mock_rotating_handler.return_value = unittest.mock.Mock()

            LoggerManager._loggers = {}

            logger = LoggerManager.setup_logger("custom_logger", "custom_prefix")

            self.assertIsInstance(logger, logging.Logger)
            self.assertEqual(logger.name, "custom_logger")
            mock_makedirs.assert_called_once_with(temp_path / "logs")
if __name__ == '__main__':
    unittest.main()