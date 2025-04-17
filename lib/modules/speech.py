import re
import time
import os
import tempfile
from gtts import gTTS
import subprocess
import logging

class SpeechToText:
    """ Class to convert text to speech with a natural-sounding voice using Google TTS """
    def __init__(self):
        """ Initialize the Google TTS engine with optimal settings for natural speech """
        # Set default language to English
        self.lang = "en"
        # Set a slow speaking rate for better clarity (False for normal speed)
        self.slow = False
        # Create a temp directory for audio files if it doesn't exist
        self.temp_dir = tempfile.gettempdir()
        # Speed factor for playback (1.0 is normal, >1.0 is faster)
        self.speed_factor = 1.15  # 15% faster than normal

    def speech(self, text):
        """ Convert text to speech using Google TTS """
        try:
            # Clean and pre-process text to improve natural flow
            processed_text = self._clean_text(text)
            
            # Break into sentences for better pacing
            sentences = self._split_into_sentences(processed_text)
            
            for i, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue
                
                # Remove any remaining punctuation that might be read aloud
                cleaned_sentence = self._remove_punctuation_for_speech(sentence)
                
                if cleaned_sentence:
                    # Create a temporary file for the audio
                    temp_file = os.path.join(self.temp_dir, f"tts_output_{i}.mp3")
                    
                    # Generate the speech audio using Google TTS
                    tts = gTTS(text=cleaned_sentence, lang=self.lang, slow=self.slow)
                    tts.save(temp_file)
                    
                    # Play the audio using the system's default audio player at faster speed
                    self._play_audio(temp_file)
                    
                    # Remove the temporary file
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                    
                    # Reduced pause between sentences for faster overall speech
                    time.sleep(0.05)
                
        except Exception as e:
            logging.error(f"Error during speech synthesis: {str(e)}")

    def _play_audio(self, audio_file):
        """Play an audio file using appropriate system command with speed adjustment"""
        try:
            # Determine the platform and use the appropriate player
            if os.name == 'posix':  # Linux or Mac
                # Try multiple players in order of preference, with speed adjustment where supported
                players = ['ffplay', 'mpg123', 'mpg321', 'mplayer']
                
                for player in players:
                    try:
                        # Check if the player is available
                        subprocess.run(['which', player], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                        
                        # Set up command based on the player with speed adjustment
                        if player == 'ffplay':
                            # ffplay supports tempo adjustment with atempo filter
                            cmd = [
                                player, 
                                '-nodisp', 
                                '-autoexit', 
                                '-loglevel', 'quiet',
                                '-af', f'atempo={self.speed_factor}',  # Speed up audio
                                audio_file
                            ]
                        elif player == 'mpg123':
                            # mpg123 supports speed with --pitch option (percentage)
                            speed_percent = int(self.speed_factor * 100)
                            cmd = [player, '--pitch', str(speed_percent), audio_file]
                        elif player == 'mplayer':
                            # mplayer supports speed with -speed option
                            cmd = [player, '-speed', str(self.speed_factor), audio_file]
                        else:
                            # For players that don't support speed adjustment
                            cmd = [player, audio_file]
                        
                        # Play the file
                        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        return
                    except subprocess.SubprocessError:
                        continue
                
                # If no player worked, try aplay as last resort (no speed adjustment)
                subprocess.run(['aplay', audio_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            elif os.name == 'nt':  # Windows
                os.startfile(audio_file)
            
            else:
                print("Unsupported platform for audio playback")
                
        except Exception as e:
            logging.error(f"Error playing audio: {str(e)}")

    def _clean_text(self, text):
        """
        Clean text to make speech sound more natural and prevent reading punctuation
        """
        # First, remove all emojis
        text = self._remove_emojis(text)
        
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        # Replace unwanted characters that might be read aloud with spaces
        text = re.sub(r'[*_~`#|<>{}[\]\\]', ' ', text)
        
        # Handle common non-alphanumeric characters properly
        replacements = {
            '+': ' plus ',
            '=': ' equals ',
            '@': ' at ',
            '&': ' and ',
            '%': ' percent ',
            '/': ' slash ',
            '...': ' ',  # Replacing ellipsis with a pause
            '--': ' ',   # Replacing double dash
            '—': ' ',    # Replacing em dash
            '–': ' ',    # Replacing en dash
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        # Expand common abbreviations that don't need regex
        common_abbr = {
            'vs.': 'versus',
            'e.g.': 'for example',
            'i.e.': 'that is',
            'etc.': 'etcetera',
            'Dr.': 'Doctor',
            'Mr.': 'Mister',
            'Mrs.': 'Misses',
            'AI': 'Artificial Intelligence',
            'UI': 'User Interface',
            'API': 'A P I',
        }
        
        for abbr, expansion in common_abbr.items():
            text = text.replace(abbr, expansion)
        
        return text
    
    def _remove_emojis(self, text):
        """Remove all emoji characters from text"""
        # Pattern to match emoji characters
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251" 
            "]+", flags=re.UNICODE
        )
        
        # Remove the emojis
        return emoji_pattern.sub(r'', text)

    def _remove_punctuation_for_speech(self, text):
        """Remove punctuation that might be read aloud"""
        # Replace punctuation likely to be spoken with spaces or nothing
        # Keep periods, question marks, etc. as they affect pacing but aren't usually spoken
        text = re.sub(r'[,;:!?()]', ' ', text)
        text = text.replace('"', '')
        text = text.replace("'", '')
        
        # Clean up any resulting multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _split_into_sentences(self, text):
        """Split text into sentences for better pacing"""
        # Basic sentence splitting - handles periods, question marks, and exclamation points
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return sentences
