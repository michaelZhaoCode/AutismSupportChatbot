"""
chatbot.py

This module provides a Chatbot class for handling chat interactions, adding PDF files, and populating PDF
files from a directory. The Chatbot class leverages clustering and embedding functionalities to
enhance responses using the BotService.
"""
import logging
import os
from collections import Counter

from constants import MAIN_MODEL_USE, MAJORITY_VOTING_N, BLURB_HISTORY, BLURB_MODEL_USE
from api.botservice import BotService
from api.servicehandler import ServiceHandler
from algos.cluster import compute_cluster, give_closest_cluster
from db_funcs.file_storage import PDFStorageInterface
from db_funcs.chat_history import ChatHistoryInterface
from db_funcs.cluster_storage import ClusterStorageInterface
from utils import extract_text, chunk_pdf_in_memory

logger = logging.getLogger(__name__)


class Chatbot:
    """
    A class to handle chat interactions, add PDF files, and populate PDF files from a directory.
    This class leverages clustering and embedding functionalities to enhance responses.

    Attributes:
        pdf_storage (PDFStorageInterface): Interface for PDF storage operations.
        chat_history (ChatHistoryInterface): Interface for chat history operations.
        cluster_storage (ClusterStorageInterface): Interface for cluster storage operations.
        botservice (BotService): BotService instance for generating embeddings and chat responses.
    """

    def __init__(
            self,
            pdf_storage: PDFStorageInterface,
            chat_history: ChatHistoryInterface,
            cluster_storage: ClusterStorageInterface,
            botservice: BotService,
            service_handler: ServiceHandler
    ):
        """
        Initializes the Chatbot with the given interfaces and BotService instance.

        Args:
            pdf_storage (PDFStorageInterface): Interface for PDF storage operations.
            chat_history (ChatHistoryInterface): Interface for chat history operations.
            cluster_storage (ClusterStorageInterface): Interface for cluster storage operations.
            botservice (BotService): BotService instance for generating embeddings and chat responses.
        """
        self.pdf_storage = pdf_storage
        self.chat_history = chat_history
        self.cluster_storage = cluster_storage
        self.botservice = botservice
        self.service_handler = service_handler

    @staticmethod
    def _load_prompt(user_type: str, response_type: str) -> str:
        """
        Load and return a corresponding prompt from a text file based on the user type and response type.

        Args:
            user_type (str): The type of user. Must be one of 'child', 'adult', or 'researcher'.
            response_type (str): The type of response format. Must be either 'rag', 'normal', or 'filter'.

        Returns:
            str: The content of the corresponding prompt file.

        Raises:
            ValueError: If the user type is not one of 'child', 'adult', or 'researcher'.
            FileNotFoundError: If the corresponding prompt file does not exist.
        """
        valid_user_types = ['child', 'adult', 'researcher']

        if user_type not in valid_user_types:
            # Not logging since an exception is explicitly raised
            raise ValueError(f"Invalid user type. Expected one of {valid_user_types}, got '{user_type}'.")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        if response_type == "filter":
            file_path = os.path.join(current_dir, 'prompts', response_type, f"prompt.txt")
        else:
            file_path = os.path.join(current_dir, 'prompts', response_type, f"{user_type}.txt")
        logger.info("_load_prompt: Searching for prompts at filepath %s", file_path)

        if not os.path.exists(file_path):
            # Not logging since an exception is explicitly raised
            raise FileNotFoundError(f"The prompt file for user type '{user_type}' does not exist at '{file_path}'.")

        with open(file_path, 'r', encoding='utf-8') as file:
            prompt = file.read()

        logger.info("_load_prompt: Found prompt for usertype %s with response type %s",
                    user_type,
                    response_type)
        return prompt

    def _classify(self, prompt):
        """
        Classify the type of response needed based on the content of the prompt.

        Args:
            prompt (str): The user's prompt to the chatbot.

        Returns:
            str: The type of response format ('rag', 'normal', or 'filter').
        """
        options = [
            "A specialized chatbot only meant to talk about autism related subjects",
            "A helpful chatbot for light topics and normal questions or discussion.",
            "A specialized chatbot that is only trained to deal with the user having thoughts of self-harm.",
            "A chatbot that has information about local services that the user wants to access."
        ]

        # Request multiple generations for majority voting.
        responses = self.botservice.choose(
            model=MAIN_MODEL_USE,
            query=f"Given the following user message, who should the user chat with?\nUser message: {prompt}",
            options=options,
            n=MAJORITY_VOTING_N  # Generate n responses for majority voting
        )

        # Since choices default to 1, responses is a list of lists, each inner list containing one option.
        # Flatten the responses to get the chosen option from each generation.
        votes = [resp[0].strip() for resp in responses if resp and resp[0].strip()]

        # Majority vote: select the option that appears most frequently.
        majority_choice, _ = Counter(votes).most_common(1)[0]

        if 'autism' in majority_choice.lower():
            print("Using RAG chatbot.")
            return 'rag'
        elif "self-harm" in majority_choice.lower():
            print("Using filter chatbot.")
            return 'filter'
        elif "service" in majority_choice.lower():
            print("Using service chatbot.")
            return 'service'
        else:
            print("Using normal chatbot.")
            return 'normal'

    def _generate(self, prompt: str, username: str, usertype: str, response_type: str, context: dict = None) -> str:
        """
        Generate a chat response using retrieval-augmented generation based on the given prompt and user's chat history.

        Args:
            prompt (str): The user's prompt to the chatbot.
            username (str): The username of the user interacting with the chatbot.
            usertype (str): The type of user interacting with the chatbot.
            response_type (str): The type of response format to use ('rag', 'normal', or 'filter').
            context (dict): Optional parameter if additional external information is needed.

        Returns:
            str: The chat response generated by the BotService.
        """
        prompt_format = self._load_prompt(usertype.lower(), response_type).format(username, prompt)

        params = {
            "model": MAIN_MODEL_USE,
            "message": prompt_format,
        }

        if response_type != "service":
            params["chat_history"] = self.chat_history.retrieve_chat_history(username)
        else:
            documents = []
            for service in context.get("services", []):
                contents = []
                # if service.address:
                #     contents.append(f"Address: {service.address}")
                if service.phone:
                    contents.append(f"Phone: {service.phone}")
                # if service.website:
                #     contents.append(f"Website: {service.website}")
                if service.distance_km is not None:
                    contents.append(f"Distance (km): {service.distance_km:.1f}")

                documents.append({
                    "title": f"{context.get('chosen_service')}: {service.service_name}",
                    "contents": "\n".join(contents)
                })
            params["documents"] = documents
            params["chat_history"] = []

        if response_type == "rag":
            closest_files = give_closest_cluster(prompt, self.botservice, self.cluster_storage)
            files_content = self.pdf_storage.retrieve_pdfs(closest_files)
            texts = [extract_text(data) for data in files_content]
            documents = [{'title': closest_files[i], 'contents': texts[i]} for i in range(len(closest_files))]
            params["documents"] = documents

        logger.info("_generate: Getting %s response", response_type)
        response = self.botservice.chat(**params)
        return response

    def chat(self, prompt: str, username: str, usertype: str, location: str = "", region_id: int = -1) -> dict:
        """
        Generate a chat response based on the given prompt and user's chat history, with optional location and regional context.

        Args:
            prompt (str): The user's prompt to the chatbot.
            username (str): The username of the user interacting with the chatbot.
            usertype (str): The type of user interacting with the chatbot.
            location (str, optional): The user's location, used to refine responses based on proximity. Defaults to an empty string.
            region_id (str, optional): A specified region id to provide additional regional context to the chatbot's response. Defaults to an empty string.

        Returns:
            str: The chat response generated by the BotService.
        """
        # TODO: have vector similarity comparison with database of commonly asked questions

        choice = self._classify(prompt)
        context = {}

        if choice == "service":
            logger.info("chat: Obtaining a response from service_handler")
            context = self.service_handler.get_response(prompt, location, region_id)

        logger.info("chat: Generating a response")
        response = self._generate(prompt, username, usertype, choice, context).replace("**", "")

        if choice == "service":
            context["services"] = [service.to_dict() for service in context["services"]]

        return {
            "response": response,
            "response_type": choice,
            "context": context
        }

    def add_pdf(self, pdf_path: str) -> None:
        """
        Add a PDF file to the database and update the cluster.

        Args:
            pdf_path (str): The path to the PDF file.
        """
        chunks = chunk_pdf_in_memory(pdf_path)
        logger.info("add_pdf: Storing chunked PDF chunks into the database")
        for chunk_name, chunk_content in chunks:
            self.pdf_storage.store_pdf_chunk(chunk_name, chunk_content)
        compute_cluster(
            files_list=[chunk[0] for chunk in chunks],
            botservice=self.botservice,
            cluster_storage=self.cluster_storage,
            pdf_storage=self.pdf_storage
        )
        logger.info("add_pdf: Cluster updated")

    def populate_pdfs(self, directory_path: str) -> None:
        """
        Add multiple PDF files from a directory to the database and update the cluster.

        Args:
            directory_path (str): The path to the directory containing PDF files.
        """
        logger.info("populate_pdfs: Adding PDFs from directory %s", directory_path)
        files_list = [os.path.join(directory_path, filename) for filename in os.listdir(directory_path)]
        all_chunks = []
        for path in files_list:
            logger.debug("populate_pdfs: Attempting to parse PDF at filepath %s", path)
            chunks = chunk_pdf_in_memory(path)
            for chunk_name, chunk_content in chunks:
                self.pdf_storage.store_pdf_chunk(chunk_name, chunk_content)
                all_chunks.append(chunk_name)
        logger.info("populate_pdfs: Completed PDF processing")
        compute_cluster(
            files_list=all_chunks,
            botservice=self.botservice,
            cluster_storage=self.cluster_storage,
            pdf_storage=self.pdf_storage
        )
        logger.info("populate_pdfs: Cluster updated")

    def update_user(self, username: str, prompt: str, response: str):
        """
        Updates the user's chat history and potentially refines their personality blurb based on the latest interactions.

        Args:
            username (str): The username whose data is being updated.
            prompt (str): The user's latest input.
            response (str): The chatbot's response.
        """
        logger.info("chat: Inserting chat history to the database")

        self.chat_history.insert_chat_history(username, [[prompt, response]])
        current_blurb = self.chat_history.retrieve_personality(username)
        history = self.chat_history.retrieve_chat_history(username)
        recent = history[-BLURB_HISTORY:] if len(history) > BLURB_HISTORY else history

        # Format chat history into a readable string
        formatted_history = "\n".join(
            f"{entry['role'].capitalize()}: {entry['content']}" for entry in recent
        )

        # Construct a prompt to refine the personality blurb
        update_prompt = f"""
        The following is a description of a user: 
        "{current_blurb}"

        Based on the last few messages in their chat history, update or expand this description 
        to reflect any new insights about their conversation style, preferences, or notable traits or information that would be useful for a chatbot to consider. 
        Only add new information if relevant. Otherwise keep it the same.
        
        Make sure to keep this very concise, only what is necessary for the use of personalizing future messages for this user.

        Chat History:
        {formatted_history}

        Provide the updated personality description:
        """

        new_blurb = self.botservice.chat(update_prompt, BLURB_MODEL_USE, [])
        self.chat_history.update_personality(username, new_blurb)

    def clear_history(self, username: str) -> None:
        """Clear the chat history for a given username."""
        self.chat_history.clear_chat_history(username)
