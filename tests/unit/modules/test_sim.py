"""Unit tests for the sim module."""
import pytest
import json
from unittest.mock import patch, MagicMock, call

from ai_tools.modules.sim import GameSimAi


@patch('ai_tools.modules.sim.SpeechToText')
@patch('ai_tools.modules.sim.Audio')
@patch('ai_tools.modules.sim.AiWrapper')
class TestGameSimAi:
    """Tests for the GameSimAi class."""

    @patch('ai_tools.modules.games.dummy_game.DummyGameWrapper')
    def test_init_default(self, mock_dummy_game, mock_ai, mock_audio, mock_speech):
        """Test initialization with default game type (dummy)."""
        # Setup mocks
        mock_dummy_instance = MagicMock()
        mock_dummy_game.return_value = mock_dummy_instance
        
        # Create GameSimAi instance
        game_sim = GameSimAi()
        
        # Verify initialization
        assert game_sim.game_type == 'dummy'
        assert game_sim.game_interface == mock_dummy_instance
        assert mock_ai.called
        assert mock_audio.called
        assert mock_speech.called
        assert mock_dummy_game.called

    @patch('ai_tools.modules.games.msfs.MSFSWrapper')
    def test_init_msfs(self, mock_msfs, mock_ai, mock_audio, mock_speech):
        """Test initialization with MSFS game type."""
        # Setup mocks
        mock_msfs_instance = MagicMock()
        mock_msfs.return_value = mock_msfs_instance
        
        # Create GameSimAi instance
        game_sim = GameSimAi(game_type='msfs')
        
        # Verify initialization
        assert game_sim.game_type == 'msfs'
        assert game_sim.game_interface == mock_msfs_instance
        assert mock_ai.called
        assert mock_audio.called
        assert mock_speech.called
        assert mock_msfs.called

    def test_init_unsupported_game(self, mock_ai, mock_audio, mock_speech):
        """Test initialization with unsupported game type."""
        with pytest.raises(ValueError, match="Unsupported game type: unknown_game"):
            GameSimAi(game_type='unknown_game')

    @patch('ai_tools.modules.sim.GameSimAi._load_game_module', side_effect=ImportError("Module not found"))
    def test_init_import_error(self, mock_load_game, mock_ai, mock_audio, mock_speech):
        """Test initialization with import error."""
        with pytest.raises(ImportError):
            GameSimAi(game_type='msfs')

    def test_start_no_game_interface(self, mock_ai, mock_audio, mock_speech):
        """Test start method with no game interface."""
        # Create GameSimAi instance with no game interface
        game_sim = GameSimAi()
        game_sim.game_interface = None
        
        # Start should return False if no game interface
        assert game_sim.start() is False

    @patch('time.sleep', return_value=None)  # Prevent sleep from causing delays
    @patch('ai_tools.modules.sim.time.time', side_effect=[0, 1, 1, 1])  # Control time progression
    def test_start_with_cleanup(self, mock_time, mock_sleep, mock_ai, mock_audio, mock_speech):
        """Test start method with cleanup."""
        # Setup mocks
        mock_audio_instance = MagicMock()
        mock_audio.return_value = mock_audio_instance
        
        # Create GameSimAi instance
        game_sim = GameSimAi()
        mock_interface = MagicMock()
        mock_interface.get_game_data.return_value = json.dumps({"test_data": "value"})
        game_sim.game_interface = mock_interface
        
        # Setup audio mock behavior to return True on check_for_audio
        # and have exit as the recognized text
        mock_audio_instance.check_for_audio.return_value = True
        mock_audio_instance.recognized_text = "exit"
        
        # Setup AI mock
        mock_ai_instance = MagicMock()
        mock_ai.return_value = mock_ai_instance
        
        # Run the test
        result = game_sim.start()
        
        # Verify behaviors
        assert result is True
        mock_interface.start_data_loop.assert_called_once()
        mock_audio_instance.init_audio.assert_called_once()
        assert mock_audio_instance.check_for_audio.called
        mock_interface.stop_data_loop.assert_called_once()

    @patch('time.sleep', return_value=None)  # Prevent sleep from causing delays
    @patch('ai_tools.modules.sim.time.time', side_effect=[0, 1, 1, 1])  # Control time progression
    def test_start_keyboard_interrupt(self, mock_time, mock_sleep, mock_ai, mock_audio, mock_speech):
        """Test start method with keyboard interrupt."""
        # Setup mocks
        mock_audio_instance = MagicMock()
        mock_audio.return_value = mock_audio_instance
        
        # Create GameSimAi instance
        game_sim = GameSimAi()
        mock_interface = MagicMock()
        # Make mock_interface.get_game_data() return a valid JSON string
        mock_interface.get_game_data.return_value = json.dumps({"test_data": "value"})
        game_sim.game_interface = mock_interface
        
        # Mock keyboard interrupt on the first check_for_audio call
        mock_audio_instance.check_for_audio.side_effect = KeyboardInterrupt()
        
        # Start the game sim
        result = game_sim.start()
        
        # Verify behaviors
        assert result is False
        mock_interface.start_data_loop.assert_called_once()
        mock_interface.stop_data_loop.assert_called_once()

    def test_cleanup_with_interface(self, mock_ai, mock_audio, mock_speech):
        """Test cleanup method with interface."""
        # Create GameSimAi instance
        game_sim = GameSimAi()
        mock_interface = MagicMock()
        game_sim.game_interface = mock_interface
        
        # Call cleanup
        game_sim.cleanup()
        
        # Verify behaviors
        mock_interface.stop_data_loop.assert_called_once()

    def test_cleanup_no_stop_method(self, mock_ai, mock_audio, mock_speech):
        """Test cleanup method with no stop_data_loop method."""
        # Create GameSimAi instance
        game_sim = GameSimAi()
        mock_interface = MagicMock()
        del mock_interface.stop_data_loop  # Remove the stop_data_loop method
        game_sim.game_interface = mock_interface
        
        # Call cleanup should not raise exceptions
        game_sim.cleanup()
        
    def test_check_warnings(self, mock_ai, mock_audio, mock_speech):
        """Test _check_warnings method."""
        # Create GameSimAi instance
        game_sim = GameSimAi()
        
        # Test with interface that doesn't have get_active_warnings
        mock_interface = MagicMock()
        del mock_interface.get_active_warnings  # Interface doesn't have the method
        game_sim.game_interface = mock_interface
        has_warning, message = game_sim._check_warnings()
        assert has_warning is False
        assert message is None
        
        # Test with interface that returns no warnings
        mock_interface = MagicMock()
        mock_interface.get_active_warnings.return_value = {}
        game_sim.game_interface = mock_interface
        has_warning, message = game_sim._check_warnings()
        assert has_warning is False
        assert message is None
        
        # Test with interface that returns warnings
        mock_interface = MagicMock()
        mock_interface.get_active_warnings.return_value = {"alerta de stall": 1}
        mock_interface.get_warning_priority.return_value = 3
        mock_interface.get_warning_message.return_value = "¡Alerta de pérdida!"
        game_sim.game_interface = mock_interface
        has_warning, message = game_sim._check_warnings()
        assert has_warning is True
        assert message == "¡Alerta de pérdida!"