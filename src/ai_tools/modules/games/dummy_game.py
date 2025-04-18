""" A Python module that provides a dummy game interface for testing """
import threading
import time
import json


class DummyGameWrapper:
    """ A dummy game interface for testing the GameSimAi functionality. """
    def __init__(self):
        self.running = False
        self.data = {}
        self.data_lock = threading.Lock()

    def fetch_game_data(self):
        """Fetches fake game data."""
        with self.data_lock:
            self.data = {
                "player": {
                    "position_x": 100.0,
                    "position_y": 200.0,
                    "position_z": 50.0,
                    "health": 100,
                    "energy": 85,
                    "speed": 10.5
                },
                "environment": {
                    "time_of_day": "day",
                    "weather": "clear",
                    "temperature": 22.5
                },
                "game_state": {
                    "score": 1250,
                    "level": 3,
                    "objective": "Find the hidden treasure"
                }
            }

    def start_data_loop(self, interval=1):
        """Starts a loop to fetch data at regular intervals."""
        self.running = True
        thread = threading.Thread(target=self._data_loop, args=(interval,), daemon=True)
        thread.start()

    def _data_loop(self, interval):
        """Thread function to fetch data in a loop."""
        while self.running:
            self.fetch_game_data()
            time.sleep(interval)

    def get_game_data(self):
        """Safely retrieves the latest game data."""
        with self.data_lock:
            return json.dumps(self.data.copy())

    def stop_data_loop(self):
        """Stops the data-fetching loop."""
        self.running = False
        
    def get_assistant_context(self):
        """Provides specialized context for the dummy game assistant."""
        return """
You are a virtual game assistant for a test game environment.
This is a dummy game used for testing the game assistant functionality.

The game data contains:
- Player information: position coordinates (x,y,z), health, energy and speed
- Environment information: time of day, weather conditions, and temperature
- Game state: current score, level number, and current objective

When responding to queries:
- Player health should be monitored (100 is maximum)
- Energy levels below 50 should be noted as low
- Temperature is in Celsius
- Position coordinates can be used for location tracking

For testing purposes, you can simulate being a helpful in-game assistant by:
- Giving status updates about the player character
- Providing hints about the current objective
- Reporting on game environmental conditions
- Suggesting strategies based on the player's current state

Remember this is a test environment, so data values remain mostly static.
"""