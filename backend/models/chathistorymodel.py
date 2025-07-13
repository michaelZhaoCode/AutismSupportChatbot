from enum import Enum


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class ChatMessage:
    """
    Represents a single message in the chat history.

    Attributes:
        role (MessageRole): The role of the sender.
        content (str): The textual content of the message.
    """

    def __init__(self, role: MessageRole, content: str):
        if not isinstance(role, MessageRole):
            raise ValueError(f"Invalid role: {role}")
        self.role = role
        self.content = content

    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role.value,
            "content": self.content
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "ChatMessage":
        role_str = data.get("role", "")
        if not MessageRole.has_value(role_str):
            raise ValueError(f"Unknown role: '{role_str}'")
        return cls(
            role=MessageRole(role_str),
            content=data.get("content", "")
        )

    def __repr__(self):
        return f"ChatMessage(role={self.role}, content='{self.content}')"


class ChatHistory:
    """
    Represents a user's chat history including optional personality notes.

    Attributes:
        username (str): The username for which the history is stored.
        messages (list of ChatMessage): The ordered messages exchanged.
    """

    def __init__(self, username, messages=None):
        self.username = username
        self.messages = messages if messages is not None else []

    def add_message(self, message):
        if isinstance(message, ChatMessage):
            self.messages.append(message)
        else:
            raise ValueError("Expected a ChatMessage instance.")

    def to_dict(self) -> list[dict[str, str]]:
        """
        Converts the chat history to a dictionary format.
        Each message is stored independently with its role and content.
        """
        return [msg.to_dict() for msg in self.messages]

    @classmethod
    def from_dict(cls, data):
        username = data.get("username", "")
        raw_history = data.get("chat_history", [])

        messages = []
        for entry in raw_history:
            if isinstance(entry, dict) and "role" in entry and "content" in entry:
                messages.append(ChatMessage.from_dict(entry))

        return cls(username=username, messages=messages)

    def __repr__(self):
        return f"ChatHistory(username='{self.username}', messages={self.messages})"

    def __len__(self):
        return len(self.messages)
        
    def __str__(self):
        """
        Returns a human-readable string representation of the chat history.
        Each message is shown with its role and content in a formatted way.
        """
        if not self.messages:
            return f"Chat history for {self.username} (empty)"
            
        lines = [f"Chat history for {self.username}:"]
        for i, msg in enumerate(self.messages, 1):
            role = msg.role.value.upper()
            # Clean up multi-line content for better readability
            content = msg.content.replace('\n', '\n    ')
            lines.append(f"{i}. [{role}]: {content}")
            
        return '\n'.join(lines)


class Personality:
    """
    Represents personality traits or conversational notes.

    Attributes:
        description (str): A textual description of the personality.
    """

    def __init__(self, description=""):
        self.description = description

    def __repr__(self):
        return f"Personality(description='{self.description}')"
