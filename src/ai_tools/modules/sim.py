""" A Python script to interact with game simulators and OpenAI GPT """
# Custom Libraries
from importlib import import_module
import json
import time
from ai_tools.modules.speech import SpeechToText
from ai_tools.modules.audio import Audio
from ai_tools.modules.ai import AiWrapper
from ai_tools.mcp.db_connector import get_vector_db


class GameSimAi:
    """A class to interact with game simulators and OpenAI GPT-4."""
    def __init__(self, game_type='dummy'):
        """ Initialize the class 
        
        Args:
            game_type (str): The type of game simulator to use. Options: 'msfs', 'iracing', 'dummy', etc.
        """
        self.game_type = game_type
        self.game_module = None
        self.game_interface = None
        self.ai = AiWrapper()
        self.audio = Audio()
        self.speech = SpeechToText()
        self.game_history = []
        self.max_history_entries = 10  # Keep last 10 game states for context
        self.active_warnings = set()  # Track currently active warnings
        self.warning_cooldown = {}  # Track warning cooldowns to avoid repetition
        self.warning_cooldown_time = 30  # Seconds between repeated warnings
        
        # Import the game module dynamically
        self._load_game_module(game_type)
        
        # Set up the base system context based on game type
        self._setup_system_context()

    def _load_game_module(self, game_type):
        """Load the appropriate game module based on the type"""
        try:
            if game_type == 'msfs':
                # Import and initialize MSFS module
                from ai_tools.modules.games.msfs import MSFSWrapper
                self.game_interface = MSFSWrapper()
            elif game_type == 'iracing':
                # Future implementation for iRacing
                # from ai_tools.modules.games.iracing import iRacingWrapper
                # self.game_interface = iRacingWrapper()
                print("iRacing support is not yet implemented")
                raise NotImplementedError("iRacing support is not yet implemented")
            elif game_type == 'dummy' or not game_type:
                # Use the dummy game for testing
                from ai_tools.modules.games.dummy_game import DummyGameWrapper
                self.game_interface = DummyGameWrapper()
                print("Using dummy game interface for testing")
            else:
                print(f"Unsupported game type: {game_type}")
                raise ValueError(f"Unsupported game type: {game_type}")
        except ImportError as e:
            print(f"Failed to import module for game type: {game_type}, error: {e}")
            raise

    def _setup_system_context(self):
        """Set up the base system context based on game type"""
        base_context = (
            "You are an intelligent in-game assistant providing real-time help and information. "
            "You will receive game data in JSON format with each query. "
            "Respond clearly and directly to the user's questions using the provided data. "
            "When asked for specific metrics or information, extract it from the data and present it clearly. "
            "Keep responses concise but informative. "
            "Highlight important warnings or critical values that might need attention. "
        )
        
        # Get additional context from the game module if available
        game_specific_context = ""
        if hasattr(self.game_interface, 'get_assistant_context'):
            game_specific_context = self.game_interface.get_assistant_context()
        
        # Combine the contexts
        self.system_base_context = base_context + " " + game_specific_context
        self.ai.set_system_base_data(self.system_base_context)

    def _store_game_data(self, game_data):
        """Store game data in history and optionally in vector database"""
        # Store in memory history
        if len(self.game_history) >= self.max_history_entries:
            self.game_history.pop(0)  # Remove oldest entry
        
        # Parse the JSON game data
        try:
            data_obj = json.loads(game_data)
            # Add timestamp
            data_obj["_timestamp"] = time.time()
            self.game_history.append(data_obj)
        except json.JSONDecodeError:
            print("Warning: Failed to decode game data JSON")
        
        # Optionally store in vector database for longer-term storage and retrieval
        try:
            vector_db = get_vector_db()
            if vector_db and vector_db.initialized:
                # Store with timestamp and game type as metadata
                vector_db.add_text(
                    game_data,
                    metadata={
                        "type": "game_data",
                        "game": self.game_type,
                        "timestamp": time.time()
                    },
                    db_name="game_data"
                )
        except Exception as e:
            # Don't crash the main flow if DB storage fails
            print(f"Warning: Failed to store game data in vector DB: {e}")

    def _prepare_game_context(self, game_data):
        """Prepare comprehensive game context for the AI"""
        context = "Current game data:\n" + game_data
        
        # Add historical context if available
        if self.game_history:
            # Calculate trends and changes from historical data
            trends = self._analyze_trends()
            if trends:
                context += "\n\nRecent trends:\n" + trends
        
        return context

    def _analyze_trends(self):
        """Analyze trends from historical data"""
        if len(self.game_history) < 2:
            return ""
        
        trends = []
        
        # This is a simplified trend analysis that should be customized based on game type
        if self.game_type == 'msfs':
            # For flight sim, analyze altitude and speed trends
            try:
                current = self.game_history[-1]
                previous = self.game_history[-2]
                
                # Altitude trend
                if "altitud de vuelo" in current and "altitud de vuelo" in previous:
                    alt_diff = current["altitud de vuelo"] - previous["altitud de vuelo"]
                    if abs(alt_diff) > 50:  # Only mention significant changes
                        direction = "increasing" if alt_diff > 0 else "decreasing"
                        trends.append(f"Altitude is {direction} at {abs(alt_diff):.1f} feet per update")
                
                # Speed trend
                if "airspeed(velocidad)" in current and "airspeed(velocidad)" in previous:
                    speed_diff = current["airspeed(velocidad)"] - previous["airspeed(velocidad)"]
                    if abs(speed_diff) > 5:  # Only mention significant changes
                        direction = "increasing" if speed_diff > 0 else "decreasing"
                        trends.append(f"Airspeed is {direction} at {abs(speed_diff):.1f} knots per update")
            except (KeyError, TypeError):
                pass  # Skip trend analysis if data structure doesn't match
        
        return "\n".join(trends)

    def _check_warnings(self):
        """Check for game warnings that need audio alerts
        
        Returns:
            tuple: (bool, str) - Whether a critical warning is active and the warning message
        """
        # Only check warnings for games that support it
        if not hasattr(self.game_interface, 'get_active_warnings'):
            return False, None
            
        # Get current active warnings
        current_warnings = self.game_interface.get_active_warnings()
        
        if not current_warnings:
            # Clear active warnings if none are currently active
            self.active_warnings = set()
            return False, None
            
        # Check for new warnings or high-priority warnings that should be repeated
        current_time = time.time()
        highest_priority = 0
        highest_priority_warning = None
        
        for warning_name in current_warnings:
            # Get warning priority
            priority = 1  # Default priority
            if hasattr(self.game_interface, 'get_warning_priority'):
                priority = self.game_interface.get_warning_priority(warning_name)
                
            # Check if this warning is new or if cooldown has expired for high priority
            is_new_warning = warning_name not in self.active_warnings
            cooldown_expired = (warning_name not in self.warning_cooldown or 
                              current_time - self.warning_cooldown[warning_name] > self.warning_cooldown_time)
            
            # Higher priority warnings get shorter cooldowns
            if priority >= 3:  # High priority
                cooldown_expired = (warning_name not in self.warning_cooldown or 
                                  current_time - self.warning_cooldown[warning_name] > 15)  # 15 seconds for high priority
            
            if (is_new_warning or cooldown_expired) and priority > highest_priority:
                highest_priority = priority
                highest_priority_warning = warning_name
                
        # Add all current warnings to the active set
        self.active_warnings.update(current_warnings.keys())
        
        # If we have a warning to announce
        if highest_priority_warning:
            # Get warning message
            warning_message = highest_priority_warning
            if hasattr(self.game_interface, 'get_warning_message'):
                warning_message = self.game_interface.get_warning_message(highest_priority_warning)
                
            # Update cooldown for this warning
            self.warning_cooldown[highest_priority_warning] = current_time
            
            return True, warning_message
            
        return False, None

    def start(self):
        """ Start the audio stream and recognize speech """
        if not self.game_interface:
            print(f"No game interface loaded for {self.game_type}")
            return False
            
        # Start the data loop for the game
        self.game_interface.start_data_loop()
        # Initialize the AI
        self.ai.initi_ai()
        # Initialize the audio
        self.audio.init_audio()

        # Track when we last fetched game data
        last_data_fetch = 0
        last_warning_check = 0
        latest_game_data = None
        latest_context = None
        
        print(f"Listening for {self.game_type} commands...", flush=True)
        try:
            while True:
                current_time = time.time()
                
                # Check if it's time to fetch new game data (every second)
                if current_time - last_data_fetch >= 1:
                    # Get and store the latest game data
                    latest_game_data = self.game_interface.get_game_data()
                    self._store_game_data(latest_game_data)
                    
                    # Prepare the latest context
                    latest_context = self._prepare_game_context(latest_game_data)
                    
                    # Update the last fetch time
                    last_data_fetch = current_time
                    
                    # Debug message (can be removed in production)
                    print(".", end="", flush=True)
                
                # Check for warnings at a regular interval (every 3 seconds)
                if current_time - last_warning_check >= 3:
                    has_warning, warning_message = self._check_warnings()
                    if has_warning and warning_message:
                        print(f"\nWARNING: {warning_message}", flush=True)
                        # Use text-to-speech to announce the warning
                        self.speech.speech(warning_message)
                    last_warning_check = current_time
                
                # Check for audio input (non-blocking)
                has_audio = self.audio.check_for_audio()
                
                if has_audio and self.audio.recognized_text != "":
                    print(f"\nRecognized: '{self.audio.recognized_text}'", flush=True)
                    
                    # Set the latest system content
                    self.ai.set_system_content(latest_context)
                    
                    # Get the AI response
                    response = self.ai.get_ai_response(self.audio.recognized_text)
                    
                    # Speak the response
                    self.speech.speech(response)

                    # Check for exit command
                    if "finalizar" in self.audio.recognized_text.lower() or "exit" in self.audio.recognized_text.lower():
                        print("Termination keyword detected. Stopping...", flush=True)
                        break
                
                # Small sleep to prevent CPU hogging
                time.sleep(0.1)
            
            return True
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources when stopping"""
        if hasattr(self.game_interface, 'stop_data_loop'):
            self.game_interface.stop_data_loop()
