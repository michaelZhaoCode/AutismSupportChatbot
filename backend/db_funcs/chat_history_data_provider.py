from abc import ABC, abstractmethod

from models.chathistorymodel import ChatHistory, ChatMessage, Personality


class ChatHistoryDataProvider(ABC):
    """
    Abstract interface for managing chat history and personality data
    using structured domain models.
    """

    @abstractmethod
    def append_chat_history(self, username: str, messages: list[ChatMessage]) -> None:
        """
        Append new chat messages to an existing user's history.

        Args:
            username (str): The username.
            messages (list[ChatMessage]): Messages to append.
        """
        pass

    @abstractmethod
    def replace_chat_history(self, username: str, chat_history: ChatHistory) -> None:
        """
        Replace the entire chat history for a user.

        Args:
            username (str): The username.
            chat_history (ChatHistory): The new chat history to store.
        """
        pass

    @abstractmethod
    def retrieve_chat_history(self, username: str) -> ChatHistory:
        """
        Retrieve the chat history for a user.

        Args:
            username (str): The username.

        Returns:
            ChatHistory: A structured chat history object.
        """
        pass

    @abstractmethod
    def clear_chat_history(self, username: str) -> None:
        """
        Delete the chat history associated with a user.

        Args:
            username (str): The username.
        """
        pass

    @abstractmethod
    def update_personality(self, username: str, personality: Personality) -> None:
        """
        Set or update a user's personality description.

        Args:
            username (str): The username.
            personality (Personality): A personality object.
        """
        pass

    @abstractmethod
    def retrieve_personality(self, username: str) -> Personality:
        """
        Retrieve a user's personality description.

        Args:
            username (str): The username.

        Returns:
            Personality: A personality object (possibly with empty description).
        """
        pass

    @abstractmethod
    def clear_personality(self, username: str) -> None:
        """
        Remove the personality data associated with a user.

        Args:
            username (str): The username.
        """
        pass
