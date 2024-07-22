"""
This module defines an abstract base class `BotService` for implementing various bot services.
"""

from abc import ABC, abstractmethod


class BotService(ABC):
    """
    An abstract base class for bot services. This class provides the structure
    for implementing various bot functionalities, including data embedding,
    conversational interaction, and option selection.

    Subclasses must implement the following methods:
    - embed(data): Embeds the given data and returns its representation.
    - chat(message): Processes the input message and returns the bot's response.
    - choose(options): Selects an option from a list of options and returns the chosen option.
    """
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Abstract method for embedding data.

        Parameters:
        data: The input data to be embedded.

        Returns:
        The embedded representation of the data.
        """
        pass

    @abstractmethod
    def chat(self, message: str, model: str, documents: dict[str, str], chat_history: list[dict[str, str]]) -> str:
        """
        Abstract method for chatting with the bot.

        Parameters:
        message: The input message to the bot.

        Returns:
        The response from the bot.
        """
        pass

    @abstractmethod
    def choose(self, options: list[str], query: str, model: str) -> str:
        """
        Abstract method for choosing from a list of options.

        Parameters:
        options: A list of options to choose from.

        Returns:
        The chosen option.
        """
        pass
