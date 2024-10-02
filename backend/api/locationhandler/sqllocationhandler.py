from api.locationhandler import LocationHandler
from abc import ABC, abstractmethod


class SQLLocationHandler(LocationHandler):
    """
    An abstract base class for handling SQL-based location operations.

    This class extends the `LocationHandler` abstract class and provides additional methods to handle
    locations using a SQL database. Methods for inserting and retrieving regions, provinces, cities,
    and services are defined here.
    """

    @abstractmethod
    def initialize_database(self) -> None:
        """
        Initializes the database for storing location-related data.
        This should set up the necessary tables and indexes.
        """
        pass

    @abstractmethod
    def insert_region(self, region: str) -> None:
        """
        Private method to insert a region into the database.

        Args:
            region (str): The name of the region to insert.
        """
        pass

    @abstractmethod
    def insert_province(self, province: str, region: str) -> None:
        """
        Inserts a province into the database.

        Args:
            province (str): The name of the province to insert.
            region (str): The region the province belongs to.
        """
        pass

    @abstractmethod
    def insert_city(self, city: str, province: str) -> None:
        """
        Inserts a city into the database.

        Args:
            city (str): The name of the city to insert.
            province (str): The province the city belongs to.
        """
        pass

    @abstractmethod
    def insert_service(self, service: str, city: str) -> None:
        """
        Inserts a service into the database for a specific city.

        Args:
            service (str): The name of the service to insert.
            city (str): The city where the service is provided.
        """
        pass

    @abstractmethod
    def find_regions_in(self, query: str) -> list[str]:
        """
        Finds and returns a list of regions based on a search query.

        Args:
            query (str): The query to search for matching regions.

        Returns:
            list: A list of region names that match the query.
        """
        pass

    @abstractmethod
    def find_all_regions(self) -> list[str]:
        """
        Retrieves all regions from the database.

        Returns:
            list: A list of all region names.
        """
        pass

    @abstractmethod
    def remove_region(self, region: str) -> None:
        """
        Removes a region from the database.

        Args:
            region (str): The name of the region to remove.
        """
        pass

    @abstractmethod
    def clear_database(self) -> None:
        """
        Clears all location data from the database.
        This should remove all entries related to regions, provinces, cities, and services.
        """
        pass