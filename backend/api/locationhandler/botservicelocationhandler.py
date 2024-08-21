"""
botservicelocationhandler.py

This module provides a concrete implementation of the LocationHandler abstract class,
leveraging a BotService to select the closest locations to a target location.

The primary class, BotServiceLocationHandler, interacts with an instance of BotService
to determine the n closest locations from a list of options by using the bot's `choose` method.
The `choose` method is guided by a query, which represents the target location,
and employs a model, defined by the constant LOCATION_MODEL_USE, to make the selection.
"""

from api.botservice import BotService
from api.locationhandler import LocationHandler
from constants import LOCATION_MODEL_USE


class BotServiceLocationHandler(LocationHandler):
    """
    BotServiceLocationHandler is a concrete implementation of LocationHandler that uses
    a BotService to find the closest locations to a target location.

    This class leverages the choose method from a BotService implementation to select
    the closest locations from a list of options, based on a query (the target location).
    """

    def __init__(self, botservice: BotService):
        """
        Initializes BotServiceLocationHandler with a given BotService instance.

        Args:
            botservice (BotService): An instance of a BotService to be used for location selection.
        """
        self.botservice = botservice

    def find_closest(self, locations: list[str], target_location: str, n: int) -> list[str]:
        """
        Finds the n closest locations to the target location using the bot service's choose method.

        Args:
            locations (list): A list of location strings to compare.
            target_location (str): The location string to which we compare the other locations.
            n (int): The number of closest locations to return.

        Returns:
            list: A list of the n closest locations to the target location.
        """

        return self.botservice.choose(
            options=locations,
            query=f"Given the following location, what are the {n} closest locations?\nLocation: {target_location}",
            model=LOCATION_MODEL_USE,
            n=n
        )
