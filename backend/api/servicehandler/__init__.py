"""
This file has a handler class for managing bot services. This class interacts with the BotService
to chat with the bot and choose services from a list of available services.
"""

import os
import random
import openpyxl

from constants import SERVICE_MODEL_USE
from constants import MAX_SERVICES
from api.botservice import BotService
from api.locationhandler import LocationHandler


class ServiceHandler:
    """
    A handler class for managing bot services. This class interacts with the BotService
    to chat with the bot and choose services from a list of available services.
    """

    def __init__(self, botservice: BotService, location_handler: LocationHandler):
        """
        Initializes the ServiceHandler with a BotService instance and loads the list of available services.

        Parameters:
        botservice (BotService): An instance of a class derived from BotService.
        """
        self.botservice = botservice
        self.location_handler = location_handler
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
        choice = self.botservice.choose(self.service_list, query, model=SERVICE_MODEL_USE)[0]
        print(f"Chosen service: {choice}")
        return choice

    def get_response(self, user_message: str, location: str) -> str:
        """
        Generates the bot's response by selecting a relevant service based on the user's message
        and utilizing the contents of the corresponding .xlsx file, if applicable, as part of the response.

        The function first chooses an appropriate service by interpreting the user's message. If the chosen
        service corresponds to an .xlsx file, the content of the file is loaded and used as a document in
        the bot's response generation. If no location is provided, random service data will be selected.

        Parameters:
        user_message (str): The input message from the user, used to determine the appropriate service.
        location (str): The location provided by the user to assist in filtering service data.

        Returns:
        str: The generated response from the bot after processing the user's message and the relevant document.
        """
        chosen_service = self.choose_service(user_message)
        service_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services', chosen_service)

        document = {"title": f"Known providers of {chosen_service}"}
        if chosen_service.endswith('.xlsx'):
            document['contents'] = self._get_service_locations(service_path, location)
        else:
            document['contents'] = ""

        prompt = self._load_prompt().format(user_message)
        response = self.botservice.chat(prompt, model=SERVICE_MODEL_USE, documents=[document], chat_history=[])
        # Remove Markdown bold
        return response.replace("**", "")

    def _get_service_locations(self, filepath: str, location: str) -> str:
        """
        Loads the contents of an .xlsx file into a single string, selecting the closest services
        based on the provided location or random services if no location is provided.

        Parameters:
        filepath (str): The path to the .xlsx file.
        location (str, optional): The location string to compare services against.

        Returns:
        str: A single string containing the concatenated content of the selected services.
        """
        wb = openpyxl.load_workbook(filepath)
        sheet = wb.active

        # Extract all addresses from the "Address" column
        rows = list(sheet.iter_rows(values_only=True))
        headers = rows[0]  # Assuming the first row is the header
        address_index = headers.index("Address")
        addresses = [row[address_index] for row in rows[1:]]

        # Determine whether to use location-based filtering or random selection
        if location:
            # Use the location_handler to find the closest services
            closest_addresses = self.location_handler.find_closest(addresses, location, MAX_SERVICES)
        else:
            # If no location is provided, pick random addresses
            closest_addresses = random.sample(addresses, min(MAX_SERVICES, len(addresses)))

        # Build content string for the selected services
        content = ""
        for row in rows[1:]:
            if row[address_index] in closest_addresses:
                row_content = ", ".join(f"{headers[i]}: {value}" for i, value in enumerate(row))
                content += row_content + " \n\n"

        return content
