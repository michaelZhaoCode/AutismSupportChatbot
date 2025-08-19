from abc import ABC, abstractmethod

class FeedbackDataProvider(ABC):
    @abstractmethod
    def add_feedback(self, username, feedback):
        """
        Add a feedback entry.

        Parameters:
            username: The name of the user providing the feedback.
            feedback: The feedback content.
        """
        pass

    @abstractmethod
    def retrieve_all_feedback(self):
        """
        Retrieve all stored feedback entries.

        Returns:
            A list of feedback entries, each represented as a dictionary
            with 'username' and 'feedback' keys.
        """
        pass

    @abstractmethod
    def clear_database(self):
        """
        Clear all feedback entries from the storage.
        """
        pass
