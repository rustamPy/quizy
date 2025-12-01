"""Main module tests"""
import pytest
from unittest.mock import patch
from quizy.main import main


class TestMain:
    """Test main function"""

    @patch("builtins.input", return_value="1")
    @patch("quizy.main.quiz_101")
    def test_main_quiz_101_selection(self, mock_101, mock_input):
        """Test main with quiz 101 selection"""
        try:
            main()
        except SystemExit:
            pass
        mock_101.start.assert_called_once()

    @patch("builtins.input", return_value="2")
    @patch("quizy.main.quiz_102")
    def test_main_quiz_102_selection(self, mock_102, mock_input):
        """Test main with quiz 102 selection"""
        try:
            main()
        except SystemExit:
            pass
        mock_102.start.assert_called_once()

    @patch("builtins.input", return_value="invalid")
    def test_main_invalid_choice(self, mock_input):
        """Test main with invalid choice"""
        with pytest.raises(SystemExit):
            main()

    @patch("builtins.input", side_effect=KeyboardInterrupt())
    def test_main_keyboard_interrupt(self, mock_input):
        """Test main with keyboard interrupt"""
        with pytest.raises(SystemExit):
            main()

    @patch("builtins.input", side_effect=EOFError())
    def test_main_eof_error(self, mock_input):
        """Test main with EOF error"""
        with pytest.raises(SystemExit):
            main()

    @patch("builtins.input", return_value="1")
    @patch("quizy.main.quiz_101")
    def test_main_quiz_101_start_called(self, mock_101, mock_input):
        """Test main calls quiz_101.start()"""
        try:
            main()
        except SystemExit:
            pass
        assert mock_101.start.called

    @patch("builtins.input", return_value="2")
    @patch("quizy.main.quiz_102")
    def test_main_quiz_102_start_called(self, mock_102, mock_input):
        """Test main calls quiz_102.start()"""
        try:
            main()
        except SystemExit:
            pass
        assert mock_102.start.called
