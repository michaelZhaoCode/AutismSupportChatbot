from abc import ABC, abstractmethod
from models.servicedata import ServiceData


class LocationDatabase(ABC):
    """
    Abstract base class for managing location data operations.

    Stores geographic data (regions, provinces, cities, and services) in a SQL database,
    providing methods for data insertion, retrieval, and deletion.
    """

    @abstractmethod
    def initialize_database(self) -> None:
        """
        Sets up the database to store location data.

        This method creates necessary tables, indexes, and any other structures
        required to support location-related data storage and retrieval.
        """
        pass

    @abstractmethod
    def insert_region(self, region: str, region_type: str, parent_id: int | None, latitude: float, longitude: float) -> bool:
        """
        Adds a region to the database. Returns if successful.

        Args:
            region (str): Identifier for the region.
            region_type (str): Type of the region (e.g., state, province).
            parent_id (int): Parent region ID to which this region belongs.
            latitude (float): Latitude coordinate of the region.
            longitude (float): Longitude coordinate of the region.
        """
        pass

    @abstractmethod
    def insert_service(self, service: str, service_type: str, region_id: int, latitude: float, longitude: float,
                       address: str = None, phone: str = None, website: str = None) -> bool:
        """
        Inserts a new service entry into the database for a specified region, with optional contact and location details.
        Returns if successful.

        Args:
            service (str): The name of the service to be added.
            service_type (str): The type of the service to be added.
            region_id (int): The geographic region ID where the service is provided.
            latitude (float): The latitude coordinate of the service's location.
            longitude (float): The longitude coordinate of the service's location.
            address (str, optional): The physical address of the service. Defaults to None.
            phone (str, optional): The contact phone number of the service. Defaults to None.
            website (str, optional): The website URL of the service. Defaults to None.
        """
        pass

    @abstractmethod
    def find_services_in(self, region_id: int, service_type: str) -> list[ServiceData]:
        """
        Retrieves a list of services available within a specified region and its subregions, optionally filtered by service type.

        Args:
            region_id (int): ID of the region to search in, including its subregions.
            service_type (str, optional): The type of service to filter results by. If not provided, retrieves all services.

        Returns:
            list[dict]: List of dictionaries, each containing details of a service available in the specified region
                        and its subregions.
        """
        pass

    @abstractmethod
    def find_all_regions(self) -> list[dict]:
        """
        Retrieves all regions stored in the database.

        Returns:
            list[dict]: List of dictionaries, each containing details for a region.
        """
        pass

    @abstractmethod
    def find_region_by_path(self, region_path: str) -> dict:
        """
        Finds and returns a region that matches a specified hierarchical path.

        Args:
            region_path (str): A comma-separated string representing a path of regions (e.g., "Country,Province,City").
                               Each region in the path should be directly related to the next.

        Returns:
            dict: A dictionary, containing details of the region that matches the path.
                                  Includes RegionID, RegionName, RegionType, ParentRegionID,
                                  Latitude, and Longitude.
        """
        pass

    @abstractmethod
    def find_region_by_id(self, region_id: int) -> dict:
        """
        Finds and returns a region that matches the specified RegionID.

        Args:
            region_id (int): The ID of the region to find.

        Returns:
            dict: A dictionary containing the details of the region, including RegionID, RegionName,
                  RegionType, ParentRegionID, Latitude, and Longitude.
                  Returns an empty dictionary if the region is not found.
        """
        pass

    @abstractmethod
    def find_all_services(self, service_type: str = None) -> list[ServiceData]:
        """
        Retrieves all services stored in the database, optionally filtered by service type.

        Args:
            service_type (str, optional): The type of services to retrieve. If None,
                                         retrieves all services.

        Returns:
            list[dict]: List of dictionaries, each containing details for a service.
        """
        pass

    @abstractmethod
    def get_all_service_types(self) -> list[str]:
        """
        Retrieves all unique service types stored in the database.

        Returns:
            list[str]: A list of unique service type names.
        """
        pass

    @abstractmethod
    def remove_region(self, region_id: int) -> bool:
        """
        Deletes a specified region from the database. Returns if successful.

        Args:
            region_id (int): ID of the region to delete.
        """
        pass

    @abstractmethod
    def remove_service(self, service_id: int) -> bool:
        """
        Deletes a specified service from the database. Returns if successful.

        Args:
            service_id (int): ID of the service to delete.
        """
        pass

    @abstractmethod
    def clear_database(self) -> None:
        """
        Removes all location-related entries from the database.

        Clears all data associated with regions, provinces, cities, and services.
        """
        pass

    @abstractmethod
    def create_snapshot(self) -> None:
        """
        Creates a snapshot of the database, storing its current state in an easily accessible format.

        This method saves the state of the database, which can be quickly accessed later by calling `load_snapshot`.
        """
        pass

    @abstractmethod
    def load_snapshot(self) -> dict:
        """
        Loads a previously created snapshot of the database in a dictionary format.

        Returns:
            dict: A dictionary representing the saved state of the database.
        """
        pass

    @abstractmethod
    def region_id(self, region: str, region_type: str) -> int | None:
        """Returns the regionID of the given region if it is present in the database.
        If not, return nothing.

        Args:
            region: The name of the region.
            region_type: The type of the region.
        """
        raise NotImplementedError
    
    @abstractmethod
    def service_id(self, lat: float, lng: float) -> int | None:
        """Returns the serviceID of the given service if it is present in the database.
        If not, return nothing.
        
        Args:
            lat: The latitude of the service's location.
            lng: The longitude of the service's location.
            """
        raise NotImplementedError
    
class RegionAlreadyExistsException(Exception):
    """Exception raised when attempting to insert a region that already exists in the database."""
    pass

class MissingParentRegionException(Exception):
    """Exception raised when attempting to insert a region with a parent id that is not present
    in the database.
    """
    pass