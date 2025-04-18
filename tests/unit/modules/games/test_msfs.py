"""Unit tests for the msfs module."""
import json
import threading
from unittest.mock import MagicMock, patch

from ai_tools.modules.games.msfs import MSFSWrapper


@patch('ai_tools.modules.games.msfs.AircraftRequests')
@patch('ai_tools.modules.games.msfs.AircraftEvents')
@patch('ai_tools.modules.games.msfs.SimConnect')
class TestMSFSWrapper:
    """Tests for the MSFSWrapper class."""

    def test_init(self, mock_simconnect, mock_events, mock_requests):
        """Test initialization of MSFSWrapper."""
        # Create mock instances
        mock_simconnect_instance = MagicMock()
        mock_simconnect.return_value = mock_simconnect_instance
        mock_events_instance = MagicMock()
        mock_events.return_value = mock_events_instance
        mock_requests_instance = MagicMock()
        mock_requests.return_value = mock_requests_instance
        
        # Initialize MSFSWrapper
        msfs = MSFSWrapper()
        
        # Verify initialization
        assert msfs.simconnect == mock_simconnect_instance
        assert msfs.requests == mock_requests_instance
        assert msfs.events == mock_events_instance
        assert msfs.running is False
        assert isinstance(msfs.data, dict)
        # Fix: Check if it has the lock attributes instead of using isinstance
        assert hasattr(msfs.data_lock, 'acquire')
        assert hasattr(msfs.data_lock, 'release')
        
        # Verify SimConnect API was initialized correctly
        mock_simconnect.assert_called_once()
        mock_events.assert_called_once_with(mock_simconnect_instance)
        mock_requests.assert_called_once_with(mock_simconnect_instance, _time=0)

    def test_fetch_flight_data(self, mock_simconnect, mock_events, mock_requests):
        """Test fetch_flight_data method."""
        # Create mock instances
        mock_requests_instance = MagicMock()
        mock_requests.return_value = mock_requests_instance
        
        # Setup mock request values
        mock_requests_instance.get.return_value = 100
        
        # Initialize and fetch data
        msfs = MSFSWrapper()
        msfs.fetch_flight_data()
        
        # Verify data was fetched
        assert len(msfs.data) > 0
        assert msfs.data["altitud de vuelo"] == 100
        assert msfs.data["velocidad vertical"] == 100
        assert msfs.requests.get.call_count > 30  # Many fields are fetched

    def test_fetch_flight_data_exception(self, mock_simconnect, mock_events, mock_requests):
        """Test fetch_flight_data method with exception."""
        # Create mock instances
        mock_requests_instance = MagicMock()
        mock_requests.return_value = mock_requests_instance
        
        # Setup mock to raise exception
        mock_requests_instance.get.side_effect = Exception("SimConnect error")
        
        # Initialize and fetch data
        msfs = MSFSWrapper()
        
        # Verify that the method handles exceptions gracefully
        with patch('builtins.print') as mock_print:
            msfs.fetch_flight_data()
            mock_print.assert_called_once_with("Error fetching data: SimConnect error")

    @patch('threading.Thread')
    def test_start_data_loop(self, mock_thread, mock_simconnect, mock_events, mock_requests):
        """Test start_data_loop method."""
        # Initialize MSFSWrapper
        msfs = MSFSWrapper()
        
        # Start data loop
        msfs.start_data_loop(interval=2)
        
        # Verify thread was started
        assert msfs.running is True
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
        
        # Verify thread arguments
        args, kwargs = mock_thread.call_args
        assert kwargs["target"] == msfs._data_loop
        assert kwargs["args"] == (2,)
        assert kwargs["daemon"] is True

    def test_get_flight_data(self, mock_simconnect, mock_events, mock_requests):
        """Test get_flight_data method."""
        # Initialize MSFSWrapper
        msfs = MSFSWrapper()
        msfs.data = {
            "altitud de vuelo": 30000,
            "velocidad vertical": 1500
        }
        
        # Get flight data
        data_json = msfs.get_flight_data()
        
        # Parse JSON and verify data
        data = json.loads(data_json)
        assert data["altitud de vuelo"] == 30000
        assert data["velocidad vertical"] == 1500

    def test_get_game_data(self, mock_simconnect, mock_events, mock_requests):
        """Test get_game_data method."""
        # Initialize MSFSWrapper
        msfs = MSFSWrapper()
        msfs.get_flight_data = MagicMock(return_value='{"test": "data"}')
        
        # Call get_game_data
        result = msfs.get_game_data()
        
        # Verify it calls get_flight_data
        msfs.get_flight_data.assert_called_once()
        assert result == '{"test": "data"}'

    def test_stop_data_loop(self, mock_simconnect, mock_events, mock_requests):
        """Test stop_data_loop method."""
        # Initialize MSFSWrapper
        msfs = MSFSWrapper()
        msfs.running = True
        
        # Stop data loop
        msfs.stop_data_loop()
        
        # Verify running flag is set to False
        assert msfs.running is False

    def test_trigger_event(self, mock_simconnect, mock_events, mock_requests):
        """Test trigger_event method."""
        # Create mock instances
        mock_events_instance = MagicMock()
        mock_events.return_value = mock_events_instance
        mock_event = MagicMock()
        mock_events_instance.find.return_value = mock_event
        
        # Initialize MSFSWrapper
        msfs = MSFSWrapper()
        
        # Trigger an event
        with patch('builtins.print') as mock_print:
            msfs.trigger_event("PARKING_BRAKES")
            
            # Verify event was triggered
            mock_events_instance.find.assert_called_once_with("PARKING_BRAKES")
            mock_event.assert_called_once()
            mock_print.assert_called_once_with("Triggered event: PARKING_BRAKES")

    def test_trigger_event_exception(self, mock_simconnect, mock_events, mock_requests):
        """Test trigger_event method with exception."""
        # Create mock instances
        mock_events_instance = MagicMock()
        mock_events.return_value = mock_events_instance
        mock_events_instance.find.side_effect = Exception("Event error")
        
        # Initialize MSFSWrapper
        msfs = MSFSWrapper()
        
        # Trigger an event with exception
        with patch('builtins.print') as mock_print:
            msfs.trigger_event("INVALID_EVENT")
            
            # Verify exception was handled
            mock_events_instance.find.assert_called_once_with("INVALID_EVENT")
            mock_print.assert_called_once_with("Error triggering event: Event error")