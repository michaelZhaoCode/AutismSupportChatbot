from abc import ABC, abstractmethod


class ServiceHandler(ABC):
    """
    An abstract base class for managing bot services. Subclasses are expected to implement
    specific methods for loading services, choosing a service based on user input, and generating
    structured responses.
    """

    @abstractmethod
    def choose_service(self, user_message: str) -> str:
        """
        Choose a service identifier based on the user's message.

        :param user_message: The user's input message.
        :return: Service type key.
        """
        pass

    @abstractmethod
    def get_response(self, user_message: str, location: str, region_id: int) -> dict:
        """
        Generate a structured response dict containing service metadata and records.

        :param user_message: The user's message guiding service selection.
        :param location: A free-form location string for geocoding.
        :param region_id: Numeric region identifier.
        :return: A list of ServiceData objects

        """
        pass
