"""
Test package containing shared test fixtures and utilities.
"""

from db_funcs.file_storage import PDFStorageInterface
from db_funcs.chat_history_data_provider import ChatHistoryDataProvider, ChatHistory, Personality
from db_funcs.cluster_storage import ClusterStorageInterface
from api.servicehandler import ServiceHandler


class DummyPDFStorage(PDFStorageInterface):
    """Dummy implementation of PDFStorageInterface for testing."""
    def __init__(self, db = None):
        pass

class DummyChatHistory(ChatHistoryDataProvider):
    """Dummy implementation of ChatHistoryDataProvider for testing."""
    def retrieve_chat_history(self, username):
        return ChatHistory(username=username, messages=[])

    def append_chat_history(self, username, messages):
        pass

    def replace_chat_history(self, username, chat_history):
        pass

    def clear_chat_history(self, username):
        pass

    def update_personality(self, username, personality):
        pass

    def retrieve_personality(self, username):
        return Personality(description="")

    def clear_personality(self, username):
        pass


class DummyClusterStorage(ClusterStorageInterface):
    def __init__(self, db = None):
        pass


class DummyServiceHandler(ServiceHandler):
    """Dummy implementation of ServiceHandler for testing."""
    def choose_service(self, user_message):
        return ""
        
    def get_response(self, user_message, location, region_id):
        return {}
