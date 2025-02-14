"""
chat_history.py

This module provides functions to insert and retrieve chat history for users in a MongoDB database.
"""
import logging
from pymongo.database import Database

logger = logging.getLogger(__name__)


class ChatHistoryInterface:
    """
    A class to interact with chat history in a MongoDB database.

    This class provides methods to insert, retrieve, and clear chat history
    for users in a MongoDB database. It requires a MongoDB database object
    to be passed during initialization.

    Attributes:
        db (Database): The MongoDB database object used for storing chat history.
    """

    def __init__(self, database: Database):
        self.db = database

    def insert_chat_history(self, username: str, new_chat_history: list[list[str]]) -> None:
        """
        Insert or update the chat history for a user in the MongoDB database.

        Args:
            username (str): The username to associate with the chat history.
            new_chat_history (list[list[str]]): A list of chat history entries, where each entry is a list containing a
                prompt and an answer.
        """
        history_collection = self.db['history']
        history_collection.create_index([("username", 1)], unique=True)

        result = history_collection.update_one(
            {'username': username},
            {'$push': {'chat_history': {'$each': new_chat_history}}},
            upsert=True
        )

        if result.matched_count == 0:
            logger.info("insert_chat_history: New user %s added", username)
        else:
            logger.info("insert_chat_history: Existing user %s updated", username)

    def retrieve_chat_history(self, username: str) -> list[dict[str, str]]:
        """
        Retrieve the chat history for a user from the MongoDB database. Note that this is structured to support the
        OpenAI GPT chat history format.

        Args:
            username (str): The username whose chat history is to be retrieved.

        Returns:
            list[dict[str, str]]: A list of dictionaries representing the chat history, where each dictionary contains a
                role ('user' or 'assistant') and the corresponding text.
        """
        history_collection = self.db['history']

        # Find the document for the given username
        document = history_collection.find_one({'username': username})

        # Check if the document was found
        if document:
            logger.info("retrieve_chat_history: Found chat history for username %s", username)
            # Return the chat history if available
            history = document['chat_history']
            formatted_history = []
            for prompt, answer in history:
                formatted_history.append({'role': 'user', 'content': prompt})
                formatted_history.append({'role': 'assistant', 'content': answer})
            logger.info("retrieve_chat_history: Returning ordered chat history between the user and assistant")
            return formatted_history

        else:
            # Return an empty list if no history is found
            logger.info("retrieve_chat_history: No chat history found for username %s; returning an empty list",
                        username)
            return []

    def clear_chat_history(self, username: str) -> None:
        """
        Clear the chat history for a specific user from the MongoDB database.

        Args:
            username (str): The username whose chat history should be cleared.
        """
        history_collection = self.db['history']

        result = history_collection.delete_one({'username': username})
        if result.deleted_count > 0:
            logger.info("clear_chat_history: Successfully cleared chat history for user %s", username)
        else:
            logger.info("clear_chat_history: No chat history found for user %s", username)

    def update_personality(self, username: str, personality: str) -> None:
        """
        Update or set the personality notes for a user.

        Args:
            username (str): The username to update.
            personality (str): A text blurb representing the user's personality or conversation style.
        """
        history_collection = self.db['history']
        history_collection.create_index([("username", 1)], unique=True)
        result = history_collection.update_one(
            {'username': username},
            {'$set': {'personality': personality}},
            upsert=True
        )
        if result.matched_count == 0:
            logger.info("update_personality: New user %s added with personality", username)
        else:
            logger.info("update_personality: Updated personality for user %s", username)

    def retrieve_personality(self, username: str) -> str:
        """
        Retrieve the personality notes for a user.

        Args:
            username (str): The username whose personality notes are to be retrieved.

        Returns:
            str: The personality text if available; otherwise, an empty string.
        """
        history_collection = self.db['history']
        document = history_collection.find_one({'username': username})
        if document and "personality" in document:
            logger.info("retrieve_personality: Found personality for username %s", username)
            return document["personality"]
        else:
            logger.info("retrieve_personality: No personality found for username %s; returning empty string", username)
            return ""

    def clear_personality(self, username: str) -> None:
        """
        Clear the personality notes for a specific user from the MongoDB database.
        This operation only clears the personality blurb, leaving chat history intact.

        Args:
            username (str): The username whose personality notes should be cleared.
        """
        history_collection = self.db['history']
        result = history_collection.update_one(
            {'username': username},
            {'$unset': {'personality': ""}}
        )
        if result.modified_count > 0:
            logger.info("clear_personality: Successfully cleared personality notes for user %s", username)
        else:
            logger.info("clear_personality: No personality notes found for user %s", username)


# Example usage:
if __name__ == "__main__":
    from utils import setup_mongo_db
    from logger import setup_logger

    setup_logger("db_funcs.log")
    db = setup_mongo_db()
    chat_history_interface = ChatHistoryInterface(db)
    chat_history_interface.insert_chat_history('boss', [['hi', 'yes']])
    chat_history_interface.insert_chat_history('boss', [['s', 'yes'], ['a', 'aaaa']])
    print(chat_history_interface.retrieve_chat_history('boss'))
    chat_history_interface.clear_chat_history('boss')
    print(chat_history_interface.retrieve_chat_history('boss'))
    chat_history_interface.clear_chat_history('boss')
