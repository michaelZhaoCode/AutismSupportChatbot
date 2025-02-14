"""
This module defines an abstract base class `BotService` for implementing various bot services.
"""

from abc import ABC, abstractmethod


class BotService(ABC):
    """
    An abstract base class that outlines the core functionality for bot services.

    This class serves as a template for implementing various bot capabilities,
    including embedding textual data, engaging in conversation, and making selections
    from a list of provided options. Subclasses inheriting from this base class
    are required to implement the following abstract methods:

    - embed(texts): Transforms a list of texts into their embedded vector representations.
    - chat(message, model, chat_history, documents): Processes a message and generates a response.
    - choose(options, query, model, n): Selects and returns the most appropriate option(s) from a list.
    """

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Transforms a list of textual data into their corresponding embedded vector representations.

        Parameters:
        texts (list[str]): A list of text strings to be embedded.

        Returns:
        list[list[float]]: A list of embedded vector representations, where each
                           sub-list corresponds to the embedded representation of a text.
        """
        pass

    @abstractmethod
    def chat(
            self,
            message: str,
            model: str,
            chat_history: list[dict[str, str]],
            documents: list[dict[str, str]] | None = None
    ) -> str:
        """
        Processes the input message and generates a conversational response based on
        the provided context, model, and optional supporting documents.

        Parameters:
        message (str): The input message from the user.
        model (str): The model used to generate the response.
        chat_history (list[dict[str, str]]): A list of prior conversation exchanges,
                                             each represented as a dictionary with keys
                                             like "user" and "bot" to maintain context.
        documents (list[dict[str, str]] | None, optional): A list of supplementary documents
                                                           that may provide additional context for the response.
                                                           Defaults to None.

        Returns:
        str: The bot's generated response as a text string.
        """
        pass

    @abstractmethod
    def choose(self, options: list[str], query: str, model: str, choices: int = 1, n: int = 1) -> list[str] | list[
        list[str]]:
        """
        Selects the most appropriate option(s) from a provided list, based on a query
        and a specified model, with the ability to return multiple selections if needed.

        Parameters:
        options (list[str]): A list of strings representing the available options.
        query (str): A query that guides the selection process.
        model (str): The model used to evaluate and make the selection.
        choices (int, optional): The number of options to select. Defaults to 1.
        n (int, optional): The number of generations to produce. Defaults to 1.

        Returns:
        list[str]: The selected option(s) if `n == 1`.
        list[list[str]]: A list of lists of selected options if `n > 1`.
        """
        pass


