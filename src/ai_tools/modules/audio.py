import json
import pyaudio
import vosk


class Audio:
    """ Class to handle audio input and output """
    def __init__(self):
        """ Initialize the PyAudio stream & vosk model """
        self.model_path = "vosk-model-es-0.42"
        self.output_file_path = "recognized_text.txt"
        self.recognized_text = ""
        self.data = None
        self.stream = None
        self.p = None
        self.model = None
        self.rec = None

    def set_model_path(self, model_path):
        """ Set the path to the Vosk model """
        self.model_path = model_path

    def init_audio(self):
        """ Initialize the audio stream """

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8192
        )

        self.model = vosk.Model(self.model_path)
        self.rec = vosk.KaldiRecognizer(self.model, 16000)

    def wait_for_audio(self):
        """ Wait for audio input """
        while True:
            self.data = self.stream.read(4096, exception_on_overflow=False)
            if self.rec.AcceptWaveform(self.data):
                result = json.loads(self.rec.Result())
                if "text" not in result:
                    continue
                if result["text"] != "":
                    self.recognized_text = result["text"]
                    print("Recognized text: " + str(self.recognized_text),
                          flush=True)
                    break
                    
    def check_for_audio(self):
        """ Non-blocking check for audio input
        
        Returns:
            bool: True if new audio was recognized, False otherwise
        """
        # Check if the stream is ready
        if not self.stream:
            return False
            
        # Read audio data without blocking
        self.data = self.stream.read(4096, exception_on_overflow=False)
        
        # Process the audio data
        if self.rec.AcceptWaveform(self.data):
            result = json.loads(self.rec.Result())
            if "text" in result and result["text"]:
                self.recognized_text = result["text"]
                return True
                
        # Return False if no new recognized text
        return False
