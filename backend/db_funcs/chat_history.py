"""
chat_history.py

This module provides functions to insert and retrieve chat history for users in a MongoDB database.
"""
from ..utils import setup


# using dict format
def insert_chat_history(username: str, new_chat_history: list[list[str]]) -> None:
    """
    Insert or update the chat history for a user in the MongoDB database.

    Args:
        username (str): The username to associate with the chat history.
        new_chat_history (list[list[str]]): A list of chat history entries, where each entry is a list containing a
            prompt and an answer.
    """
    db = setup()
    history_collection = db['history']
    db.fs.files.create_index([('username', 1)], unique=True)

    result = history_collection.update_one(
        {'username': username},
        {'$push': {'chat_history': {'$each': new_chat_history}}},
        upsert=True
    )
    if result.matched_count == 0:
        print("New user added.")
    else:
        print("Existing user updated.")


def retrieve_chat_history(username: str) -> list[dict[str, str]]:
    """
    Retrieve the chat history for a user from the MongoDB database.

    Args:
        username (str): The username whose chat history is to be retrieved.

    Returns:
        list[dict[str, str]]: A list of dictionaries representing the chat history, where each dictionary contains a
            role ('USER' or 'CHATBOT') and the corresponding text.
    """
    db = setup()
    history_collection = db['history']

    # Find the document for the given username
    document = history_collection.find_one({'username': username})

    # Check if the document was found
    if document:
        # Return the chat history if available
        history = document['chat_history']
        formatted_history = []
        for prompt, answer in history:
            formatted_history.append({'role': 'USER', 'text': prompt})
            formatted_history.append({'role': 'CHATBOT', 'text': answer})
        return formatted_history

    else:
        # Return an empty list if no history is found
        print(f"No chat history found for username: {username}")
        return []

# insert_chat_history('boss', [['hi', 'yes']])
# insert_chat_history('boss', [['s', 'yes'], ['a', 'aaaa']])
# print(retrieve_chat_history('boss'))
