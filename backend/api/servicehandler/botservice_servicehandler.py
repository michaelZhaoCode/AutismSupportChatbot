"""
This file has a handler class for managing bot services. This class interacts with the BotService
to chat with the bot and choose services from a list of available services.
"""

import os
import random
from math import radians, sin, cos, sqrt, atan2

from constants import SERVICE_MODEL_USE
from constants import MAX_SERVICES
from api.botservice import BotService
from api.locationdatabase import LocationDatabase
from api.servicehandler import ServiceHandler


class BotserviceServiceHandler(ServiceHandler):
    """
    A handler class for managing bot services. This class interacts with the BotService
    to chat with the bot and choose services from a list of available services.
    """

    def __init__(self, botservice: BotService, location_database: LocationDatabase):
        """
        Initializes the ServiceHandler with a BotService instance and loads the list of available services.

        Parameters:
        botservice (BotService): An instance of a class derived from BotService.
        """
        self.botservice = botservice
        self.location_database = location_database
        self._load_services()

    def _load_services(self):
        """
        Loads the list of available services from the 'services' directory.

        Returns:
        list[str]: A list of filenames representing available services.
        """
        # TODO: add logging

        self.service_list = self.location_database.get_all_service_types()

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
        # TODO: add logging

        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "..", 'prompts', "service", f"prompt.txt")

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
        # TODO: add logging

        query = f"Based on this user message, what type of service do they require? User message: {user_message}"
        choice = self.botservice.choose(self.service_list, query, model=SERVICE_MODEL_USE)[0]
        print(f"Chosen service: {choice}")
        return choice

    def get_response(self, user_message: str, location: str, region_id: int = -1) -> str:
        """
        Generates a response by selecting and processing service data based on the user's message and location.

        The function first interprets the user's message to determine an appropriate service category. It then uses
        the location, if provided, to refine the search within `self.location_database`. If no location is specified,
        random service data may be selected. Latitude and longitude are estimated for the location via a prompt,
        and the bot compiles a list of relevant service providers in the specified region.

        Parameters:
            user_message (str): The user's input message, which guides the service selection.
            location (str): The user's location, used to filter services by geographic proximity.
            region_id (int): A specified regional id for further narrowing down services by region.

        Returns:
            str: The bot's generated response after processing the user's message and the selected service data.
        """
        # TODO: add logging

        chosen_service = self.choose_service(user_message)

        if location:
            location_prompt = f"Provide the estimated latitude and longitude values of this location, " \
                              f"for your output format, only provide the two values separated by a " \
                              f"single comma with nothing else.\nLocation: {location}"

            try:
                latitude, longitude = self.botservice.chat(location_prompt, model=SERVICE_MODEL_USE,
                                                           chat_history=[]).split(",")
                latitude = float(latitude.strip())
                longitude = float(longitude.strip())
            except ValueError:
                latitude, longitude = None, None
        else:
            latitude, longitude = None, None

        document = {"title": f"Known providers of {chosen_service}",
                    'contents': self._find_services(chosen_service, MAX_SERVICES, region_id, latitude, longitude)}

        prompt = self._load_prompt().format(user_message)
        response = self.botservice.chat(prompt, model=SERVICE_MODEL_USE, documents=[document], chat_history=[])
        # Remove Markdown bold
        return response.replace("**", "")

    def _find_services(self, service_type: str, n: int, region_id: int = -1, latitude: float = None,
                       longitude: float = None) -> str:

        # Step 1: Check if region_path is provided
        if region_id > -1:
            region = self.location_database.find_region_by_id(region_id)
            if not region:
                return "Region not found."

            # Use region's latitude and longitude if not provided
            if latitude is None and longitude is None:
                latitude = region['Latitude']
                longitude = region['Longitude']
        else:
            region_id = None  # No region bound

        # Step 2: Fetch services based on region
        if region_id:
            services = self.location_database.find_services_in(region_id, service_type)
        else:
            services = self.location_database.find_all_services(service_type)

        # Step 3: Filter and sort services by distance if lat/long is given
        if latitude is not None and longitude is not None:
            services = sorted(
                services,
                key=lambda s: self._haversine_distance(latitude, longitude, s['Latitude'], s['Longitude'])
            )
        elif region_id == -1 and latitude is None and longitude is None:
            # Step 4: Select random services if no location data is provided
            services = random.sample(services, min(n, len(services)))

        # Step 5: Select the top n closest services
        closest_services = services[:n]

        # Step 6: Concatenate service information for the return string
        result = "\n\n".join(
            f"Service Name: {service['ServiceName']}\n"
            f"Address: {service.get('Address', 'N/A')}\n"
            f"Phone: {service.get('Phone', 'N/A')}\n"
            f"Website: {service.get('Website', 'N/A')}"
            for service in closest_services
        )
        return result

    # Haversine distance helper function
    @staticmethod
    def _haversine_distance(lat1, lon1, lat2, lon2):
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        r = 6371  # Radius of Earth in kilometers
        return r * c
