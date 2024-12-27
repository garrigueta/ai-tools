import pyttsx3


class SpeechToText:
    """ Class to convert text to speech """
    def __init__(self):
        """ Initialize the pyttsx3 engine """
        self.engine = pyttsx3.init()

    def speech(self, text):
        """ Convert text to speech """
        self.engine.say(text)
        self.engine.runAndWait()
        self.engine.stop()

    def change_voice(self, id):
        """ Change the voice of the pyttsx3 engine """
        self.engine.setProperty('voice', id)
        return True

    def get_voices(self):
        """ Get the list of id of voices available """
        voice_ids = []
        voices = self.engine.getProperty('voices')
        for voice in voices:
            voice_ids.append(voice.id)
        return voices
