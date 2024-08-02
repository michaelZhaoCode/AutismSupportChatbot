"""
This file has a handler class for managing bot services. This class interacts with the BotService
to chat with the bot and choose services from a list of available services.
"""

import os
import openpyxl

from constants import SERVICE_MODEL_USE
from constants import MAX_SERVICES
from api.botservice import BotService


class ServiceHandler:
    """
    A handler class for managing bot services. This class interacts with the BotService
    to chat with the bot and choose services from a list of available services.
    """

    def __init__(self, botservice: BotService):
        """
        Initializes the ServiceHandler with a BotService instance and loads the list of available services.

        Parameters:
        botservice (BotService): An instance of a class derived from BotService.
        """
        self.botservice = botservice
        self._load_services()

    def _load_services(self):
        """
        Loads the list of available services from the 'services' directory.

        Returns:
        list[str]: A list of filenames representing available services.
        """
        self.service_list = []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        services_file_path = os.path.join(current_dir, 'services')
        for filename in os.listdir(services_file_path):
            if os.path.isfile(os.path.join(services_file_path, filename)):
                self.service_list.append(filename)

    @staticmethod
    def _load_prompt() -> str:
        """
        Loads a prompt from a text file located in the 'prompts/service' directory
        relative to the current file. If the file does not exist, a FileNotFoundError
        is raised.

        Returns:
            str: The content of the prompt file.

        Raises:
            FileNotFoundError: If the prompt file does not exist at the specified path.
        """

        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'prompts', "service", f"prompt.txt")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The prompt file does not exist at '{file_path}'.")

        with open(file_path, 'r', encoding='utf-8') as file:
            prompt = file.read()

        print(f"Found prompt with response type: service")

        return prompt

    def choose_service(self, user_message: str) -> str:
        """
        Chooses a service from the available services based on the user's message.

        Parameters:
        user_message (str): The message from the user.

        Returns:
        str: The chosen service filename.
        """
        query = f"Based on this user message, what type of service do they require? User message: {user_message}"
        choice = self.botservice.choose(self.service_list, query, model=SERVICE_MODEL_USE)
        print(f"Chosen service: {choice}")
        return choice

    def get_response(self, user_message: str) -> str:
        """
        Gets the bot's response by first choosing an appropriate service based on the user's message and
        then loading the corresponding .xlsx sheet to use its contents as the document.

        Parameters:
        user_message (str): The message from the user.

        Returns:
        str: The response from the bot.
        """
        chosen_service = self.choose_service(user_message)
        service_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services', chosen_service)

        document = {"title": f"Known providers of {chosen_service}"}
        if chosen_service.endswith('.xlsx'):
            document['contents'] = self._load_xlsx(service_path)
        else:
            document['contents'] = ""

        prompt = self._load_prompt().format(user_message)
        response = self.botservice.chat(prompt, model=SERVICE_MODEL_USE, documents=[document], chat_history=[])
        # Remove markdown bold
        return response.replace("**", "")

    @staticmethod
    def _load_xlsx(filepath: str) -> str:
        """
        Loads the contents of an .xlsx file into a single string.

        Parameters:
        filepath (str): The path to the .xlsx file.

        Returns:
        str: A single string containing the concatenated content of the .xlsx file.
        """
        wb = openpyxl.load_workbook(filepath)
        content = ""
        for sheet in wb:
            rows = list(sheet.iter_rows(values_only=True))
            headers = rows[0]
            for row in rows[1:MAX_SERVICES + 1]:
                row_content = ", ".join(f"{headers[i]}: {value}" for i, value in enumerate(row))
                content += row_content + " \n\n"
        return content
