# pylint: disable=missing-module-docstring, redefined-outer-name
import os

from openai import OpenAI
import pytest

from api.botservice.gpt_botservice import GPTBotService
from constants import SERVICE_MODEL_USE


@pytest.fixture
def bot_service():
    api_key = os.environ["OPENAI_API_KEY"]
    openai_client = OpenAI(api_key=api_key)
    return GPTBotService(openai_client)


@pytest.fixture
def options():
    return [
        "A specialized chatbot only meant to talk about autism related"
        " subjects",
        "A helpful chatbot for light topics and normal questions or "
        "discussion.",
        "A specialized chatbot that is only trained to deal with the user "
        "having thoughts of self-harm.",
        "A chatbot that has information about local services that the user "
        "wants to access."
    ]


@pytest.fixture
def query():
    return (
        "Given the following user message, who should the user chat with?\n"
        "User message: "
    )


@pytest.mark.parametrize("prompt",
    [
        "I think I might be autistic. How can I tell?",
        "Do you have tips for handling sensory overload?",
        "Why do I struggle with eye contact so much?",
        "I'm having trouble understanding sarcasm. Is that normal?",
        "Why do I have to pretend to be normal to everybody else?"
])
def test_choose_autism(bot_service, options, query, prompt):
    selected = bot_service.choose(
        model=SERVICE_MODEL_USE,
        query=query + prompt,
        options=options,
    )[0]

    assert "autism" in selected.lower()


@pytest.mark.parametrize("prompt",
    [
        "Yo, what's up?",
        "Tell me a fun fact!",
        "What's the weather like today?",
        "Can you help me with a random question?",
        "I just watched a great movie! Have you seen it?"
])
def test_choose_normal(bot_service, options, query, prompt):
    selected = bot_service.choose(
        model=SERVICE_MODEL_USE,
        query=query + prompt,
        options=options,
    )[0]

    assert "normal" in selected.lower()


@pytest.mark.parametrize("prompt",
    [
        "I don't think I can do this anymore.",
        "I keep thinking about hurting myself.",
        "Nothing feels worth it right now.",
        "I need someone to talk to, I feel really low.",
        "Do you have coping strategies for when I feel like this?"
])
def test_choose_self_harm(bot_service, options, query, prompt):
    selected = bot_service.choose(
        model=SERVICE_MODEL_USE,
        query=query + prompt,
        options=options,
    )[0]

    assert "self-harm" in selected.lower()


@pytest.mark.parametrize("prompt",
    [
        "Where can I find a therapist near me?",
        "Are there any autism support groups in my area?",
        "What mental health hotlines are available right now?",
        "Can you help me find disability accommodations in my city?",
        "I need a dentist. Any recommendations?"
])
def test_choose_services(bot_service, options, query, prompt):
    selected = bot_service.choose(
        model=SERVICE_MODEL_USE,
        query=query + prompt,
        options=options,
    )[0]

    assert "services" in selected.lower()
