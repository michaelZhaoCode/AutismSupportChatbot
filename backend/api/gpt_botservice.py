"""
This module provides a concrete implementation of the abstract base class `BotService`.
The `GPTBotService` class uses a GPT-based model to implement functionalities for
embedding data, interacting with the bot, and choosing from a list of options.

The `GPTBotService` class contains the following methods:
1. `embed` - Embeds a list of texts and returns their representations.
2. `chat` - Processes an input message and returns the bot's response.
3. `choose` - Selects an option from a list of options based on a query, using a specified GPT model.
"""

from api.botservice import BotService
from openai import OpenAI


class GPTBotService(BotService):
    """
    A concrete implementation of the BotService abstract base class that uses a GPT model
    to provide the functionalities of embedding data, interacting with the bot,
    and choosing from a list of options.
    """

    def __init__(self, openai_client: OpenAI):
        self.openai_client = openai_client

    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Embeds the given data using a GPT-based model.

        Parameters:
        texts: The input texts to be embedded.

        Returns:
        The embedded representation of the texts.
        """

        response = self.openai_client.embeddings.create(
            input=texts,
            model="text-embedding-3-small"
        )

        return [embedding_obj.embedding for embedding_obj in response.data]

    def chat(
            self,
            message: str,
            model: str,
            chat_history: list[dict[str, str]],
            documents: list[dict[str, str]] | None = None
    ) -> str:
        """
        Processes the input message and returns the bot's response using a GPT-based model.

        Parameters:
        message: The input message to the bot.
        model: The GPT model to be used for generating the response.
        documents: A list of document dictiona to be used as context.
        chat_history: The history of the chat for context.

        Returns:
        The response from the bot.
        """
        context_str = ""
        if documents:
            context_str += "Here are some documents to use as context for your response:\n"
            for document in documents:
                context_str += f"Document Name: {document['title']}\n\nDocument Contents: {document['contents']}\n\n"
        context_str += message

        latest_message = {"role": "user", "content": context_str}
        chat_history.append(latest_message)
        print(chat_history)
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=chat_history
        )

        return response.choices[0].message.content

    def choose(self, options: list[str], query: str, model: str) -> str:
        """
        Selects an option from a list of options using a GPT-based model.

        Parameters:
        options: A list of options to choose from.
        query: The query to determine the choice.
        model: The GPT model to be used for making the choice.

        Returns:
        The chosen option.
        """
        instruct = ("You are to select an option that best fits the query given to you. Respond only with one of the "
                    "options provided.")
        chat_history = [
            {"role": "system", "content": instruct}
        ]
        prompt = query + "\nOptions:\n"
        for option in options:
            prompt += option + "\n"
        chat_history.append({"role": "user", "content": prompt})

        response = self.openai_client.chat.completions.create(
            model=model,
            messages=chat_history
        )

        return response.choices[0].message.content
