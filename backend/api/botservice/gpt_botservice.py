"""
This module provides a concrete implementation of the abstract base class `BotService`.
The `GPTBotService` class uses a GPT-based model to implement functionalities for
embedding data, interacting with the bot, and choosing from a list of options.

The `GPTBotService` class contains the following methods:
1. `embed` - Embeds a list of texts and returns their representations.
2. `chat` - Processes an input message and returns the bot's response.
3. `choose` - Selects an option from a list of options based on a query, using a specified GPT model.
"""
import logging

from api.botservice import BotService
from openai import OpenAI

logger = logging.getLogger(__name__)


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
        logger.info("embed: creating embeddings with GPT model")
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
        documents: A list of document dictionaries to be used as context.
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
        logger.debug("chat: Added related contextual documents for the GPT model")

        latest_message = {"role": "user", "content": context_str}
        chat_history.append(latest_message)
        logger.debug("chat: Added latest message to chat history")
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=chat_history
        )
        logger.info("chat: Obtained response from GPT model")

        return response.choices[0].message.content

    def choose(self, options: list[str], query: str, model: str, n: int = 1) -> list[str]:
        """
        Selects an option from a list of options using a GPT-based model.

        Parameters:
        options: A list of options to choose from.
        query: The query to determine the choice.
        model: The GPT model to be used for making the choice.
        n: The amount of options to choose from

        Returns:
        The n chosen options.
        """
        if n == 1:
            instruct = ("You are to select an option that best fits the query given to you. Respond only with one of "
                        "the options provided.")
        else:
            instruct = (f"You are to select the top {n} options that best fit the query given to you. Respond only "
                        f"with your chosen options out of those provided, each on new lines.")
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
        logger.info("choose: Obtained response from GPT model")
        logger.debug("choose: response=%s", response.choices[0].message.content)

        return response.choices[0].message.content.split('\n')
