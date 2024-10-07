from abc import ABC, abstractmethod


class ServiceHandler(ABC):
    """
    An abstract base class for managing bot services. Subclasses are expected to implement
    specific methods for loading services, choosing a service based on user input, and generating responses.
    """

    @abstractmethod
    def choose_service(self, user_message: str) -> str:
        """
        Abstract method to choose a service from available options based on the user's message.
        
        Parameters:
            user_message (str): The input message from the user.

        Returns:
            str: The chosen service identifier.
        """
        pass

    @abstractmethod
    def get_response(self, user_message: str, location: str) -> str:
        """
        Abstract method to generate a response based on the chosen service and user message.

        Parameters:
            user_message (str): The input message from the user.
            location (str): The user's location to filter service data.

        Returns:
            str: The generated response from the bot.
        """
        pass
