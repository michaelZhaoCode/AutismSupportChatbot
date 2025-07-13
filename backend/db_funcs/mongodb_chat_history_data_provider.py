"""
mongodb_chat_history_data_provider.py

This module implements the ChatHistoryDataProvider interface using MongoDB.
"""

import logging
from pymongo.database import Database
from models.chathistorymodel import ChatMessage, ChatHistory, Personality
from db_funcs.chat_history_data_provider import ChatHistoryDataProvider

logger = logging.getLogger(__name__)


class MongoDBChatHistoryProvider(ChatHistoryDataProvider):
    """
    MongoDB implementation of the ChatHistoryDataProvider interface.
    """

    def __init__(self, database: Database):
        self.db = database
        self.collection = self.db['history']
        self.collection.create_index([("username", 1)], unique=True)

    def append_chat_history(self, username: str, messages: list[ChatMessage]) -> None:
        if not messages:
            return

        existing_doc = self.collection.find_one({"username": username})
        existing_history = existing_doc.get("chat_history", []) if existing_doc else []

        # Append new messages to existing messages
        new_entries = [msg.to_dict() for msg in messages]
        updated_history = existing_history + new_entries

        result = self.collection.update_one(
            {"username": username},
            {"$set": {"chat_history": updated_history}},
            upsert=True
        )

        logger.info("append_chat_history: Chat history updated for user %s", username)

    def replace_chat_history(self, username: str, chat_history: ChatHistory) -> None:
        messages = [msg.to_dict() for msg in chat_history.messages]

        result = self.collection.update_one(
            {"username": username},
            {"$set": {"chat_history": messages}},
            upsert=True
        )

        logger.info("replace_chat_history: Chat history replaced for user %s", username)

    def retrieve_chat_history(self, username: str) -> ChatHistory:
        document = self.collection.find_one({"username": username})
        if not document or "chat_history" not in document:
            logger.info("retrieve_chat_history: No history found for user %s", username)
            return ChatHistory(username=username)

        messages = [ChatMessage.from_dict(entry) for entry in document["chat_history"]]
        logger.info("retrieve_chat_history: Retrieved %d messages for user %s", len(messages), username)
        return ChatHistory(username=username, messages=messages)

    def clear_chat_history(self, username: str) -> None:
        result = self.collection.update_one(
            {"username": username},
            {"$unset": {"chat_history": ""}}
        )
        if result.modified_count > 0:
            logger.info("clear_chat_history: Cleared chat history for user %s", username)
        else:
            logger.info("clear_chat_history: No chat history to clear for user %s", username)

    def update_personality(self, username: str, personality: Personality) -> None:
        result = self.collection.update_one(
            {"username": username},
            {"$set": {"personality": personality.description}},
            upsert=True
        )
        logger.info("update_personality: Personality updated for user %s", username)

    def retrieve_personality(self, username: str) -> Personality:
        document = self.collection.find_one({"username": username})
        if document and "personality" in document:
            logger.info("retrieve_personality: Found personality for user %s", username)
            return Personality(description=document["personality"])

        logger.info("retrieve_personality: No personality found for user %s", username)
        return Personality()

    def clear_personality(self, username: str) -> None:
        result = self.collection.update_one(
            {"username": username},
            {"$unset": {"personality": ""}}
        )
        if result.modified_count > 0:
            logger.info("clear_personality: Cleared personality for user %s", username)
        else:
            logger.info("clear_personality: No personality to clear for user %s", username)


# Example usage:
if __name__ == "__main__":
    from utils import setup_mongo_db
    from logger import setup_logger

    setup_logger("db_funcs.log")
    db = setup_mongo_db()
    chat_history_interface = MongoDBChatHistoryProvider(db)
    print(chat_history_interface.retrieve_personality("User"))
    print(chat_history_interface.retrieve_chat_history("User"))
