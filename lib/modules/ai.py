import os
from openai import OpenAI


class AiWrapper(object):
    """ Wrapper for the OpenAI API """
    def __init__(self):
        self.client = None
        self.system_base_data = (
            "Eres un asistente de vuelo, " +
            "recibes la información en formato JSON, " +
            "me debes proporcionar el dato cuando te la pida, " +
            "Si te pregunto un dato solo envía el dato, "
            "solo quiero que reportes datos con 2 decimales. ")
        self.system_content = ""
        self.user_content = ""
        self.ai_response = ""

    def set_system_content(self, system_content):
        """ Set the system content """
        self.system_content = system_content

    def set_user_content(self, user_content):
        """ Set the user content """
        self.user_content = user_content

    def set_system_base_data(self, system_base_data):
        """ Set the system base data """
        self.system_base_data = system_base_data

    def initi_ai(self):
        """ Initialize the OpenAI API client """
        self.client = OpenAI(
            organization=os.getenv("OPENAI_ORG"),
            project=os.getenv("OPENAI_PROJ"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    def ai_request(self):
        """ Send the text to the OpenAI API and return the response """
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                    {"role": "system", "content":
                     self.system_base_data +
                     self.system_content},
                    {"role": "user", "content": self.user_content}
                ],
        )
        self.ai_response = str(response.choices[0].message.content)

    def get_ai_response(self, message, system_content=None):
        """ Get the AI response """
        if system_content is not None:
            self.set_system_content(system_content)
        self.set_user_content(message)
        self.ai_request()
        return self.ai_response
