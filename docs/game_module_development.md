# Game Module Development Guide for AI-Tools

This document provides comprehensive guidance on how to create custom game modules for the AI-Tools framework. Game modules allow the AI assistant to interface with different games and simulators, providing real-time data and voice-based interactions.

## Table of Contents

1. [Overview](#overview)
2. [Game Module Architecture](#game-module-architecture)
3. [Required Interface](#required-interface)
4. [Optional Interface](#optional-interface)
5. [Data Structure](#data-structure)
6. [Game-Specific AI Context](#game-specific-ai-context)
7. [Warnings System](#warnings-system)
8. [Testing Your Module](#testing-your-module)
9. [Examples](#examples)
10. [Integration with AI-Tools](#integration-with-ai-tools)

## Overview

Game modules in AI-Tools serve as interfaces between games/simulators and the AI assistant system. They continuously collect game data, provide it to the AI for context, and can optionally trigger game events. The system uses these modules to create an interactive voice-activated AI assistant that understands the game state and can respond to player queries in real-time.

## Game Module Architecture

A game module consists of a single class that encapsulates all interactions with the target game. The class should be placed in the `src/ai_tools/modules/games/` directory and follow this naming pattern:

- Module file name: `your_game_name.py`
- Class name: `YourGameNameWrapper`

For example, `msfs.py` contains the `MSFSWrapper` class for Microsoft Flight Simulator.

## Required Interface

Your game module class must implement these core methods to work with the GameSimAi system:

```python
class YourGameNameWrapper:
    def __init__(self):
        self.running = False
        self.data = {}
        self.data_lock = threading.Lock()
        # Initialize your game connection here
        
    def fetch_game_data(self):
        """
        Fetch current data from the game and store it in self.data.
        This method should update self.data with the latest game state.
        
        Implementation example:
        with self.data_lock:
            self.data = {
                "player": {
                    "health": 100,
                    "position_x": 123.4,
                    # Other game-specific data
                }
            }
        """
        pass
        
    def get_game_data(self):
        """
        Return the current game data as a JSON string.
        
        Implementation example:
        with self.data_lock:
            return json.dumps(self.data.copy())
        """
        pass
        
    def start_data_loop(self, interval=1):
        """
        Start a background thread that calls fetch_game_data at regular intervals.
        
        Implementation example:
        self.running = True
        thread = threading.Thread(target=self._data_loop, args=(interval,), daemon=True)
        thread.start()
        """
        pass
        
    def _data_loop(self, interval):
        """
        Background thread function that calls fetch_game_data periodically.
        
        Implementation example:
        while self.running:
            self.fetch_game_data()
            time.sleep(interval)
        """
        pass
        
    def stop_data_loop(self):
        """
        Stop the data collection thread.
        
        Implementation example:
        self.running = False
        """
        pass
```

## Optional Interface

These methods can be implemented to provide enhanced functionality:

```python
class YourGameNameWrapper:
    # Required methods as above...
    
    def get_assistant_context(self):
        """
        Provide game-specific context to the AI assistant.
        This text will be added to the AI's system prompt.
        
        Return a string with information about your game that helps the AI
        understand how to interpret the data and respond appropriately.
        
        Example:
        return """
        You are a virtual assistant for [Game Name].
        The player health ranges from 0-100, where:
        - 0-20: Critical condition
        - 21-50: Wounded
        - 51-100: Healthy
        
        Key terminology:
        - HP: Health points
        - MP: Magic points
        - XP: Experience points
        """
        """
        pass
        
    def trigger_event(self, event_name):
        """
        Trigger an event in the game based on its name.
        This allows the AI to control game functions.
        
        Example:
        try:
            # Game-specific code to trigger an event
            print(f"Triggered event: {event_name}")
        except Exception as e:
            print(f"Error triggering event: {e}")
        """
        pass
        
    def get_active_warnings(self):
        """
        Return a list of active warnings from the game.
        These will be announced to the player.
        
        Example:
        warnings = []
        if self.data.get("player", {}).get("health", 100) < 20:
            warnings.append("low_health")
        return warnings
        """
        pass
        
    def get_warning_message(self, warning_name):
        """
        Return a human-readable message for a specific warning.
        
        Example:
        warnings_info = {
            "low_health": "Warning! Health critically low. Seek medical attention.",
            "low_ammo": "Warning! Ammunition running low."
        }
        return warnings_info.get(warning_name, f"Warning: {warning_name}")
        """
        pass
        
    def get_warning_priority(self, warning_name):
        """
        Return the priority level for a specific warning (1-10).
        Higher numbers indicate more urgent warnings.
        
        Example:
        priorities = {
            "low_health": 9,
            "low_ammo": 5
        }
        return priorities.get(warning_name, 5)  # Default priority is 5
        """
        pass
```

## Data Structure

The game data should be structured as a dictionary that can be converted to JSON. This data will be provided to the AI assistant as context when responding to user queries. There's no strict schema, but you should structure it logically for your specific game. The data should be comprehensive enough to answer common player questions but not overwhelmingly large.

Example structure:

```python
self.data = {
    "player": {
        "name": "Player1",
        "health": 85,
        "position": {
            "x": 123.45,
            "y": 67.89,
            "z": 45.67
        },
        "equipment": {
            "weapon": "Laser Sword",
            "armor": "Shield Generator"
        }
    },
    "environment": {
        "location": "Desert Planet",
        "time": "Day",
        "weather": "Sandstorm"
    },
    "game_state": {
        "mission": "Retrieve the ancient artifact",
        "progress": 75,
        "difficulty": "Hard"
    },
    "warnings": {
        "low_health": false,
        "low_ammo": true
    }
}
```

## Game-Specific AI Context

The `get_assistant_context()` method is crucial for providing game-specific knowledge to the AI. This context should include:

1. **Value Ranges & Interpretations**: What constitutes a "normal" or "dangerous" value for key metrics
2. **Terminology**: Common abbreviations and terms used in the game
3. **Response Guidance**: How the AI should format or prioritize information
4. **Game Specifics**: Any unique aspects of your game the AI should know about

This context is added to the AI's system prompt, which guides how it interprets game data and formulates responses.

Example for a flight simulator:

```python
def get_assistant_context(self):
    return """
    You are a virtual co-pilot for a flight simulator.
    
    Key flight parameters:
    - Normal airspeed: 80-250 knots
    - Normal climb/descent rate: -2000 to +2000 feet per minute
    - Safe altitude depends on terrain, but should be at least 1000 feet AGL
    
    Key terminology:
    - AGL: Above Ground Level
    - MSL: Mean Sea Level
    - HDG: Heading
    - ALT: Altitude
    - IAS: Indicated Airspeed
    
    When reporting flight data:
    - Round altitude to the nearest 100 feet
    - Report heading as a three-digit number (e.g., "heading zero-nine-zero")
    - Always prioritize any active warnings in your responses
    """
```

## Warnings System

The warnings system allows your game module to proactively alert players to critical conditions. To implement warnings:

1. The `get_active_warnings()` method should return a list of string identifiers for currently active warnings
2. The `get_warning_message(warning_name)` method should return a user-friendly message for each warning
3. The `get_warning_priority(warning_name)` method should return an integer from 1-10 indicating urgency

Warnings will be announced by text-to-speech and have a cooldown period (default 30 seconds) before being repeated.

## Testing Your Module

Create a unit test file in the `tests/unit/modules/games/` directory that tests all your module's methods. You should use mocking to simulate the game's API rather than requiring the actual game for tests.

Test structure example:

```python
@patch('your.game.api.GameAPI')
class TestYourGameWrapper:
    def test_init(self, mock_game_api):
        # Test initialization
        game = YourGameWrapper()
        assert hasattr(game, 'data_lock')
        mock_game_api.assert_called_once()
        
    def test_fetch_game_data(self, mock_game_api):
        # Test data fetching
        mock_instance = mock_game_api.return_value
        mock_instance.get_player_health.return_value = 75
        
        game = YourGameWrapper()
        game.fetch_game_data()
        
        assert game.data["player"]["health"] == 75
```

## Examples

Two example implementations are available in the codebase:

1. `dummy_game.py`: A simple implementation that generates fake game data for testing
2. `msfs.py`: Microsoft Flight Simulator integration using the SimConnect API

Study these examples to understand how to structure your own game module.

## Integration with AI-Tools

Once your game module is created, you need to register it in the `GameSimAi` class in `src/ai_tools/modules/sim.py`. Add an entry to the `_load_game_module()` method:

```python
def _load_game_module(self, game_type):
    try:
        if game_type == 'msfs':
            from ai_tools.modules.games.msfs import MSFSWrapper
            self.game_interface = MSFSWrapper()
        elif game_type == 'your_game_id':
            from ai_tools.modules.games.your_game import YourGameWrapper
            self.game_interface = YourGameWrapper()
        elif game_type == 'dummy' or not game_type:
            from ai_tools.modules.games.dummy_game import DummyGameWrapper
            self.game_interface = DummyGameWrapper()
        else:
            print(f"Unsupported game type: {game_type}")
            raise ValueError(f"Unsupported game type: {game_type}")
    except ImportError as e:
        print(f"Failed to import module for game type: {game_type}, error: {e}")
        raise
```

Users will then be able to start your game module with:

```bash
aitools sim your_game_id start
```

Happy game module development!