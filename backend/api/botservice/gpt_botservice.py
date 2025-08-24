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
from models.chathistorymodel import ChatHistory, MessageRole

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

    async def async_llm_generate(self, query_prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Async wrapper for OpenAI API calls for web search integration.
        This wraps the synchronous OpenAI client in an async function.
        """
        import asyncio
        
        loop = asyncio.get_event_loop()
        
        def sync_call():
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": query_prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        
        return await loop.run_in_executor(None, sync_call)

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
            chat_history: ChatHistory | None = None,
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
        if not chat_history:
            chat_history = [latest_message]
        else:
            chat_history = chat_history.to_dict()
            chat_history = self._convert_role_keys(chat_history)

            chat_history.append(latest_message)
        logger.debug("chat: Added latest message to chat history")
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=chat_history
        )
        logger.info("chat: Obtained response from GPT model")

        return response.choices[0].message.content

    @staticmethod
    def _convert_role_keys(chat_history: list[dict[str, str]]) -> list[dict[str, str]]:
        """
        Converts the role values in the chat history to OpenAI's format.
        """
        for message in chat_history:
            if message["role"] == MessageRole.USER.value:
                message["role"] = "user"
            elif message["role"] == MessageRole.ASSISTANT.value:
                message["role"] = "assistant"
        return chat_history

    def choose(self, options: list[str], query: str, model: str, choices: int = 1, n: int = 1) -> list[str] | list[
        list[str]]:
        """
        Selects one or more options from a list of options using a GPT-based model.

        Parameters:
        options: A list of options to choose from.
        query: The query to determine the choice.
        model: The GPT model to be used for making the choice.
        choices: The number of options to select.
        n: The number of generations to produce.

        Returns:
        A list of selected options if n == 1.
        A list of lists of selected options if n > 1.
        """
        if choices == 1:
            instruct = ("You are to select an option that best fits the query given to you. Respond only with one of "
                        "the options provided.")
        else:
            instruct = (
                f"You are to select the top {choices} options that best fit the query given to you. Respond only "
                f"with your chosen options out of those provided, each on a new line.")

        chat_history = [
            {"role": "system", "content": instruct}
        ]
        prompt = query + "\nOptions:\n" + "\n".join(options)
        chat_history.append({"role": "user", "content": prompt})

        response = self.openai_client.chat.completions.create(
            model=model,
            messages=chat_history,
            n=n  # Generate multiple responses if needed
        )
        logger.info("choose: Obtained response from GPT model")
        logger.debug("choose: response=%s", response.choices)

        # Extract results from response
        results = [choice.message.content.split("\n") for choice in response.choices]

        # Return a flat list if n == 1, otherwise return a list of lists
        return results[0] if n == 1 else results
