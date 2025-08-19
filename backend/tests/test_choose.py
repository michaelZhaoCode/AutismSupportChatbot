"""
Tests for the chatbot's classification functionality.

These tests verify that the chatbot correctly routes messages to the appropriate handler
based on the message content. The expected output is one of: 'rag', 'normal', 'service', or 'filter'.
"""
# pylint: disable=missing-module-docstring, redefined-outer-name

import os
import pytest
import dotenv
from openai import OpenAI
from api.chatbot import Chatbot
from api.botservice.gpt_botservice import GPTBotService

# Import dummy classes from tests package
from tests import DummyPDFStorage, DummyChatHistory, DummyClusterStorage, DummyServiceHandler

dotenv.load_dotenv()

@pytest.fixture
def chatbot():
    """Create a chatbot instance with dummy dependencies for testing."""
    api_key = os.environ["OPENAI_API_KEY"]
    openai_client = GPTBotService(openai_client=OpenAI(api_key=api_key))
    return Chatbot(
        pdf_storage=DummyPDFStorage(),
        chat_history=DummyChatHistory(),
        cluster_storage=DummyClusterStorage(),
        botservice=openai_client,
        service_handler=DummyServiceHandler()
    )


TEST_CASES = [
    # RAG (autism-related) test cases
    ("I think I might be autistic. How can I tell?", "rag"),
    ("Do you have tips for handling sensory overload?", "rag"),
    ("Why do I struggle with eye contact so much?", "rag"),
    ("I'm having trouble understanding sarcasm. Is that normal?", "rag"),
    ("Why do I have to pretend to be normal to everybody else?", "rag"),
    
    # Normal conversation test cases
    ("Yo, what's up?", "normal"),
    ("Tell me a fun fact!", "normal"),
    ("What's the weather like today?", "normal"),
    ("Can you help me with a random question?", "normal"),
    ("I just watched a great movie! Have you seen it?", "normal"),
    
    # Filter (self-harm) test cases
    ("I don't think I can do this anymore.", "filter"),
    ("I keep thinking about hurting myself.", "filter"),
    ("Nothing feels worth it right now.", "filter"),
    ("I need someone to talk to, I feel really low.", "filter"),
    ("Do you have coping strategies for when I feel like this?", "filter"),
    
    # Service-related test cases
    ("Where can I find a therapist near me?", "service"),
    ("Are there any autism support groups in my area?", "service"),
    ("What mental health hotlines are available right now?", "service"),
    ("Can you help me find disability accommodations in my city?", "service"),
    ("I need a dentist. Any recommendations?", "service"),
]


@pytest.mark.parametrize("prompt,expected_label", TEST_CASES)
def test_chatbot_classification(chatbot, prompt, expected_label):
    """Test that the chatbot correctly classifies different types of messages."""
    result = chatbot.classify(prompt)
    assert result == expected_label, f"Expected {expected_label} for prompt: {prompt}"
