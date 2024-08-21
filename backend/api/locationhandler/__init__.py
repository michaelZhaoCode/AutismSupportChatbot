from abc import ABC, abstractmethod

"""
location_handler.py

This module defines an abstract base class `LocationHandler` which provides a blueprint for location-based 
operations. The primary function of this class is to define a method for finding the closest locations from 
a list of location strings, based on a comparison with a target location. Subclasses should implement the 
`find_closest` method to provide concrete behavior.
"""


class LocationHandler(ABC):
    """
    An abstract base class for handling location-based operations.

    This class defines a blueprint for subclasses to implement the `find_closest` method, which should
    return the n closest locations to a given target location from a list of locations.

    Methods:
        find_closest(locations: list, target_location: str, n: int) -> list:
            Abstract method that must be implemented by subclasses to find the n closest locations
            to the target location.
    """
    @abstractmethod
    def find_closest(self, locations: list[str], target_location: str, n: int) -> list[str]:
        """
        Abstract method to find the n closest locations to the target location.

        Args:
            locations (list): A list of location strings to compare.
            target_location (str): The location string to which we compare the other locations.
            n (int): The number of closest locations to return.

        Returns:
            list: A list of the n closest locations to the target location.
        """
        pass
