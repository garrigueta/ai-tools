"""Unit tests for the dummy_game module."""
import json
import threading
import time
from unittest.mock import MagicMock, patch

from ai_tools.modules.games.dummy_game import DummyGameWrapper


class TestDummyGameWrapper:
    """Tests for the DummyGameWrapper class."""

    def test_init(self):
        """Test initialization of DummyGameWrapper."""
        dummy_game = DummyGameWrapper()
        
        assert dummy_game.running is False
        assert isinstance(dummy_game.data, dict)
        assert isinstance(dummy_game.data_lock, threading.Lock)

    def test_fetch_game_data(self):
        """Test fetch_game_data method."""
        dummy_game = DummyGameWrapper()
        
        # Initially the data should be empty
        assert dummy_game.data == {}
        
        # Fetch data
        dummy_game.fetch_game_data()
        
        # Verify data is populated
        assert "player" in dummy_game.data
        assert "environment" in dummy_game.data
        assert "game_state" in dummy_game.data
        
        # Verify specific data points
        assert dummy_game.data["player"]["health"] == 100
        assert dummy_game.data["environment"]["weather"] == "clear"
        assert dummy_game.data["game_state"]["objective"] == "Find the hidden treasure"

    @patch('threading.Thread')
    def test_start_data_loop(self, mock_thread):
        """Test start_data_loop method."""
        dummy_game = DummyGameWrapper()
        
        # Start the data loop
        dummy_game.start_data_loop(interval=2)
        
        # Verify thread was started with correct arguments
        assert dummy_game.running is True
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
        
        # Verify thread arguments
        args, kwargs = mock_thread.call_args
        assert kwargs["target"] == dummy_game._data_loop
        assert kwargs["args"] == (2,)
        assert kwargs["daemon"] is True

    def test_data_loop(self):
        """Test _data_loop method."""
        dummy_game = DummyGameWrapper()
        dummy_game.fetch_game_data = MagicMock()
        
        # Set up to run loop only once
        dummy_game.running = True
        
        def stop_after_one_iteration():
            time.sleep(0.1)
            dummy_game.running = False
        
        # Start a thread to stop the loop
        stop_thread = threading.Thread(target=stop_after_one_iteration)
        stop_thread.start()
        
        # Run the data loop
        dummy_game._data_loop(interval=0.05)
        
        # Verify fetch_game_data was called
        dummy_game.fetch_game_data.assert_called()
        
        # Clean up
        stop_thread.join()

    def test_get_game_data(self):
        """Test get_game_data method."""
        dummy_game = DummyGameWrapper()
        dummy_game.data = {
            "player": {"health": 100},
            "test": "value"
        }
        
        # Get the game data
        data_json = dummy_game.get_game_data()
        
        # Parse the JSON
        data = json.loads(data_json)
        
        # Verify data
        assert data["player"]["health"] == 100
        assert data["test"] == "value"

    def test_stop_data_loop(self):
        """Test stop_data_loop method."""
        dummy_game = DummyGameWrapper()
        dummy_game.running = True
        
        # Stop the data loop
        dummy_game.stop_data_loop()
        
        # Verify running flag is set to False
        assert dummy_game.running is False