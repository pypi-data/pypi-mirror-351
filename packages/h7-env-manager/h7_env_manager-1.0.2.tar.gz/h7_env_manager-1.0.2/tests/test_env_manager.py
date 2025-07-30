import unittest
import os
import sys
from unittest.mock import patch

# Add the src directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from h7_env_manager import EnvManager

class TestEnvManager(unittest.TestCase):
    
    @patch('h7_env_manager.env_manager.os.getenv')
    @patch('h7_env_manager.env_manager._dotenv_loaded', True)  # Skip loading dotenv
    def test_get_required_env_var_success(self, mock_getenv):
        """Test that get_required_env_var returns the value when found"""
        mock_getenv.return_value = "test_value"
        value = EnvManager.get_required_env_var("TEST_VAR")
        self.assertEqual(value, "test_value")
        mock_getenv.assert_called_once_with("TEST_VAR")
    
    @patch('h7_env_manager.env_manager.os.getenv')
    @patch('h7_env_manager.env_manager._dotenv_loaded', True)  # Skip loading dotenv
    def test_get_required_env_var_not_found(self, mock_getenv):
        """Test that get_required_env_var raises ValueError when not found"""
        mock_getenv.return_value = None
        with self.assertRaises(ValueError):
            EnvManager.get_required_env_var("MISSING_VAR")
    
    @patch('h7_env_manager.env_manager.os.getenv')
    @patch('h7_env_manager.env_manager._dotenv_loaded', True)  # Skip loading dotenv
    def test_get_optional_env_var_with_default(self, mock_getenv):
        """Test that get_optional_env_var returns default when var not found"""
        mock_getenv.return_value = None
        value = EnvManager.get_optional_env_var("MISSING_VAR", "default_value")
        self.assertEqual(value, "default_value")
        mock_getenv.assert_called()
        mock_getenv.assert_called_once_with("MISSING_VAR")

    @patch("h7_env_manager.env_manager.EnvManager.get_optional_env_var")
    @patch("h7_env_manager.env_manager._dotenv_loaded", True)  # Skip loading dotenv
    def test_get_optional_bool_env_var_true(self, mock_get_optional):
        """Test that get_optional_bool_env_var returns True when var is 'true'"""
        mock_get_optional.return_value = "true"
        result = EnvManager.get_optional_bool_env_var("BOOL_VAR", False)
        self.assertTrue(result)
        mock_get_optional.assert_called()
        mock_get_optional.assert_called_once_with("BOOL_VAR")

    @patch("h7_env_manager.env_manager.EnvManager.get_optional_env_var")
    @patch("h7_env_manager.env_manager._dotenv_loaded", True)  # Skip loading dotenv
    def test_get_optional_bool_env_var_false(self, mock_get_optional):
        """Test that get_optional_bool_env_var returns False when var is not 'true'"""
        mock_get_optional.return_value = "false"
        result = EnvManager.get_optional_bool_env_var("BOOL_VAR", True)
        self.assertFalse(result)
        mock_get_optional.assert_called_once_with("BOOL_VAR")

    @patch("h7_env_manager.env_manager.EnvManager.get_optional_env_var")
    @patch("h7_env_manager.env_manager._dotenv_loaded", True)  # Skip loading dotenv
    def test_get_optional_bool_env_var_missing(self, mock_get_optional):
        """Test that get_optional_bool_env_var returns default when var is missing"""
        mock_get_optional.return_value = None
        result = EnvManager.get_optional_bool_env_var("MISSING_VAR", True)
        self.assertTrue(result)
        mock_get_optional.assert_called_once_with("MISSING_VAR")

    @patch("h7_env_manager.env_manager.EnvManager.get_optional_env_var")
    @patch("h7_env_manager.env_manager._dotenv_loaded", True)  # Skip loading dotenv
    def test_get_optional_bool_env_var_empty(self, mock_get_optional):
        """Test that get_optional_bool_env_var returns default when var is empty string"""
        mock_get_optional.return_value = ""
        result = EnvManager.get_optional_bool_env_var("EMPTY_VAR", False)
        self.assertFalse(result)
        mock_get_optional.assert_called_once_with("EMPTY_VAR")

    @patch("h7_env_manager.env_manager.EnvManager.get_optional_env_var")
    @patch("h7_env_manager.env_manager._dotenv_loaded", True)  # Skip loading dotenv
    def test_get_optional_bool_env_var_case_insensitive(self, mock_get_optional):
        """Test that get_optional_bool_env_var handles case insensitively"""
        mock_get_optional.return_value = "TRUE"
        result = EnvManager.get_optional_bool_env_var("BOOL_VAR", False)
        self.assertTrue(result)
        mock_get_optional.assert_called_once_with("BOOL_VAR")



if __name__ == '__main__':
    unittest.main()
