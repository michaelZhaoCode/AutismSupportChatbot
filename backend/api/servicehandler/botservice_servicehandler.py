"""
This file has a handler class for managing bot services. This class interacts with the BotService
to chat with the bot and choose services from a list of available services.
"""

import random
import logging
from math import radians, sin, cos, sqrt, atan2

from constants import SERVICE_MODEL_USE
from constants import MAX_SERVICES_RECOMMENDED
from api.botservice import BotService
from api.locationdatabase import LocationDatabase
from api.servicehandler import ServiceHandler


logger = logging.getLogger(__name__)


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
        logger.info("Chosen service: %s", choice)

        return choice

    def get_response(self, user_message: str, location: str, region_id: int = -1) -> dict:
        """
        Generate a structured response dict containing:
          - chosen_service (str): The service type selected.
          - max_services (int): The maximum number of services returned.
          - latitude (float or None): Geocoded latitude of the provided location.
          - longitude (float or None): Geocoded longitude of the provided location.
          - services (list of ServiceData)
        """
        # TODO: add logging

        chosen_service = self.choose_service(user_message)

        coords = self._get_coordinates(location) if location else None

        logger.info("Coordinates for location '%s': %s", location, coords)

        services = self._find_services(
            chosen_service, MAX_SERVICES_RECOMMENDED, region_id, coords
        )
        logger.info("Found %d services", len(services))

        return {
            "chosen_service": chosen_service,
            "max_services": MAX_SERVICES_RECOMMENDED,
            "latitude": coords[0] if coords else None,
            "longitude": coords[1] if coords else None,
            "services": services
        }

    def _find_services(
            self,
            service_type: str,
            n: int,
            region_id: int = -1,
            lat_long: tuple[float, float] | None = None
    ) -> list[dict]:
        # if a valid region_id is provided, use its coordinates as fallback
        if region_id > -1:
            region = self.location_database.find_region_by_id(region_id)
            if not region:
                return []
            if not lat_long:
                latitude = region["Latitude"]
                longitude = region["Longitude"]
        else:
            region_id = None

        # fetch raw services
        if region_id is not None:
            candidates = self.location_database.find_services_in(region_id, service_type)
        else:
            candidates = self.location_database.find_all_services(service_type)

        top = []
        # if we have coordinates, sort by distance
        if lat_long:
            latitude, longitude = lat_long
            top = sorted(candidates,
                         key=lambda s: self._haversine_distance(
                             latitude, longitude, s.latitude, s.longitude
                         )
                         )[:n]
        # otherwise, pick random sample if no location or region
        elif region_id is None:
            top = random.sample(candidates, min(n, len(candidates)))

        # optionally, compute and attach distance
        if lat_long:
            for service in top:
                lat, lon = lat_long
                service_lat = service.latitude
                service_lon = service.longitude
                service.distance_km = self._haversine_distance(lat, lon, service_lat, service_lon)

        return top

    def _get_coordinates(self, location: str) -> tuple[float, float] | None:
        """
        Geocode a free-form location string into (latitude, longitude).

        :param location: The location to geocode.
        :return: Tuple of floats or None on failure.
        """
        prompt = (
            "Provide the estimated latitude and longitude values of this location;"
            " output only two values separated by a comma.\n"
            f"Location: {location}"
        )
        try:
            lat_str, lon_str = self.botservice.chat(
                prompt, model=SERVICE_MODEL_USE, chat_history=[]
            ).split(",")
            return float(lat_str), float(lon_str)
        except ValueError:
            return None

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
