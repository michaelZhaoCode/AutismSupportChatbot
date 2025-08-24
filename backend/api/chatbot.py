"""
chatbot.py

This module provides a Chatbot class for handling chat interactions, adding PDF files, and populating PDF
files from a directory. The Chatbot uses Pinecone for storing and retrieving PDF chunks with embeddings.
"""
import logging
import os
from collections import Counter

from constants import MAIN_MODEL_USE, MAJORITY_VOTING_N, BLURB_HISTORY_CONTEXT, BLURB_MODEL_USE
from api.botservice import BotService
from api.servicehandler import ServiceHandler
from api.websearch.async_web_search_service import AsyncWebSearchService
import asyncio


from db_funcs.unified_pinecone_storage import UnifiedPineconeStorage
from models.chathistorymodel import ChatMessage, Personality, MessageRole
from db_funcs.chat_history_data_provider import ChatHistoryDataProvider
from utils import extract_text, chunk_pdf_in_memory

logger = logging.getLogger(__name__)
from dotenv import load_dotenv
load_dotenv()
class Chatbot:
    """
    A class to handle chat interactions, add PDF files, and populate PDF files from a directory.
    This class uses Pinecone for storing and retrieving PDF chunks with embeddings.

    Attributes:
        storage (UnifiedPineconeStorage): Unified storage for PDF chunks and embeddings.
        chat_history (ChatHistoryInterface): Interface for chat history operations.
        botservice (BotService): BotService instance for generating embeddings and chat responses.
        service_handler (ServiceHandler): Handler for service-related queries.
    """

    def __init__(
            self,
            storage: UnifiedPineconeStorage,
            chat_history: ChatHistoryDataProvider,
            botservice: BotService,
            service_handler: ServiceHandler
    ):
        """
        Initializes the Chatbot with the given storage and service instances.

        Args:
            pdf_storage (PDFStorageInterface): Interface for PDF storage operations.
            chat_history (ChatHistoryDataProvider): Interface for chat history operations.
            cluster_storage (ClusterStorageInterface): Interface for cluster storage operations.
            feedback_storage (FeedbackDataProvider): Interface for feedback storage operations.
            botservice (BotService): BotService instance for generating embeddings and chat responses.
            service_handler (ServiceHandler): Handler for service-related queries.
        """
        self.storage = storage
        self.chat_history = chat_history
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
            raise ValueError(f"Invalid user type. Expected one of {valid_user_types}, got '{user_type}'.")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        if response_type == "filter":
            file_path = os.path.join(current_dir, 'prompts', response_type, f"prompt.txt")
        else:
            file_path = os.path.join(current_dir, 'prompts', response_type, f"{user_type}.txt")
        logger.info("_load_prompt: Searching for prompts at filepath %s", file_path)

        if not os.path.exists(file_path):
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


    def _should_use_web_search(self, prompt: str, response_type: str) -> bool:
        """
        Analyze the prompt to determine if web search would be beneficial.
        
        Args:
            prompt (str): The user's prompt to analyze.
            response_type (str): The type of response ('rag', 'normal', 'filter', 'service').
            
        Returns:
            bool: True if web search should be used, False otherwise.
        """
        if response_type in ['filter', 'service']:
            return False

        options = [
            "A question that would benefit from current, up-to-date information from the internet",
            "A question that can be answered with existing knowledge and doesn't need web search"
        ]

        try:
            classification_prompt = (
                "Analyze this user message to determine if it would benefit from current web search results.\n"
                "Consider web search beneficial for:\n"
                "- Questions about recent events, news, or current developments\n"
                "- Questions about specific current programs, services, or resources\n"
                "- Questions requiring up-to-date statistics, research, or medical information\n"
                "- Questions about current policies, regulations, or guidelines\n"
                "- Questions about specific locations, businesses, or services that might have changed\n\n"
                "Don't use web search for:\n"
                "- General conversational questions\n"
                "- Basic explanations of concepts that don't change frequently\n"
                "- Personal advice that doesn't require current information\n"
                "- Questions already well-covered by existing knowledge\n\n"
                f"User message: {prompt}"
            )

            responses = self.botservice.choose(
                model=MAIN_MODEL_USE,
                query=classification_prompt,
                options=options,
                n=MAJORITY_VOTING_N
            )

            # Flatten responses and count votes
            votes = [resp[0].strip() for resp in responses if resp and resp[0].strip()]
            majority_choice, _ = Counter(votes).most_common(1)[0]
            print(votes, majority_choice)

            should_search = "current" in majority_choice.lower() and "internet" in majority_choice.lower()
            logger.info(
                f"_should_use_web_search: {'Enabling' if should_search else 'Skipping'} web search "
                f"for prompt: {prompt[:100]}..."
            )
            return should_search

        except Exception as e:
            logger.error(f"_should_use_web_search: Error analyzing prompt: {e}")
            return False


    def _generate(self, prompt: str, username: str, usertype: str, response_type: str, context: dict = None, web_search_results: list[dict] = None) -> str:
        """
        Generate a chat response using retrieval-augmented generation based on the given prompt and user's chat history.

        Args:
            user_message (str): The user's prompt to the chatbot.
            username (str): The username of the user interacting with the chatbot.
            usertype (str): The type of user interacting with the chatbot.
            response_type (str): The type of response format to use ('rag', 'normal', or 'filter').
            context (dict): Optional parameter if additional external information is needed.
            web_search_results (list[dict]): Optional web search results to enhance the response.

        Returns:
            str: The chat response generated by the BotService.
        """
        prompt_format = self._load_prompt(usertype.lower(), response_type).format(username, user_message)

        params = {
            "model": MAIN_MODEL_USE,
            "message": prompt_format,
        }

        # Collect all documents (RAG, service, and web search)
        all_documents = []

        if response_type != "service":
            # Convert ChatHistory to the format expected by the chat service
            chat_history = self.chat_history.retrieve_chat_history(username)
            params["chat_history"] = chat_history
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
            all_documents.extend(documents)
            params["chat_history"] = []  # No history for service responses

        if response_type == "rag":

            # Get relevant chunks using similarity search
            relevant_chunks = self.storage.get_relevant_chunks(self.botservice.embed(texts=[prompt])[0], top_k=5)
            if relevant_chunks:
                # Format chunks as documents for the model
                documents = [
                    {'title': chunk_id, 'contents': chunk_text}
                    for chunk_id, chunk_text in relevant_chunks
                ]
                all_documents.extend(documents)
                logger.info(f"_generate: Using {len(documents)} relevant documents for RAG")

        # Add web search results if available
        if web_search_results:
            all_documents.extend(web_search_results)
            logger.info(f"_generate: Adding {len(web_search_results)} web search results")

        # Set combined documents
        if all_documents:
            params["documents"] = all_documents


        logger.info("_generate: Getting %s response", response_type)
        response = self.botservice.chat(**params)
        return response

    def chat(self, prompt: str, username: str, usertype: str, location: str = "", region_id: int = -1) -> dict:
        """
        Generate a chat response based on the given prompt and user's chat history, with optional location and regional context.

        Args:
            user_message (str): The user's prompt to the chatbot.
            username (str): The username of the user interacting with the chatbot.
            usertype (str): The type of user interacting with the chatbot.
            location (str, optional): The user's location, used to refine responses based on proximity. Defaults to an empty string.
            region_id (str, optional): A specified region id to provide additional regional context to the chatbot's response. Defaults to an empty string.

        Returns:
            dict: The chat response generated by the BotService with web search results if needed.
        """
        choice = self._classify(prompt)
        
        context = {}
        web_search_results = None

        if choice == "service":
            logger.info("chat: Obtaining a response from service_handler")
            context = self.service_handler.get_response(user_message, location, region_id)

        # Determine if web search should be performed based on prompt analysis
        should_search = self._should_use_web_search(prompt, choice)
        if should_search:
            
            logger.info("chat: Performing web search to enhance response")
            try:
                web_search_results = asyncio.run(self._perform_web_search(prompt))
                logger.info(f"chat: Found {len(web_search_results)} web search results")
            except Exception as e:
                logger.error(f"chat: Web search failed: {e}")
                web_search_results = []

        logger.info("chat: Generating a response")

        response = self._generate(prompt, username, usertype, choice, context, web_search_results).replace("**", "")


        if choice == "service":
            context["services"] = [service.to_dict() for service in context["services"]]

        return {
            "response": response,
            "response_type": choice,
            "context": context
        }

    async def _perform_web_search(self, prompt: str) -> list[dict]:
        """
        Perform web search asynchronously to enhance chatbot responses.
        
        Args:
            prompt (str): The user's prompt to search for
            
        Returns:
            list[dict]: Formatted web search results for LLM consumption
        """
        try:
            # Create web search service instance
            web_search_service = AsyncWebSearchService(
                num_search_queries=2,
                num_results_per_query=3,
                max_concurrent_requests=10,
            )
            
            # Perform search and content extraction
            search_results = await web_search_service.search_and_extract(
                prompt, 
                self.botservice.async_llm_generate
            )
            
            return search_results
            
        except Exception as e:
            logger.error(f"_perform_web_search: Error during web search: {e}")
            return []

    def add_pdf(self, pdf_path: str) -> None:
        """
        Add a PDF file to Pinecone storage.

        Args:
            pdf_path (str): The path to the PDF file.
        """
        # Chunk the PDF
        chunks = chunk_pdf_in_memory(pdf_path)
        # Prepare chunks data with embeddings
        chunks_data = []
        for chunk_name, chunk_content in chunks:
            # Extract text from chunk
            chunk_text = extract_text(chunk_content)
            
            # Generate embedding for the chunk
            embedding = self.botservice.embed(texts=[chunk_text])[0]
            
            # Add to chunks data
            chunks_data.append((chunk_name, chunk_text, embedding))
        
        # Store all chunks with embeddings in Pinecone
        self.storage.store_pdf_chunks(chunks_data)

    def populate_pdfs(self, directory_path: str) -> None:
        """
        Add multiple PDF files from a directory to Pinecone storage.

        Args:
            directory_path (str): The path to the directory containing PDF files.
        """
        logger.info("populate_pdfs: Adding PDFs from directory %s", directory_path)
        files_list = [os.path.join(directory_path, filename) for filename in os.listdir(directory_path) if filename.endswith('.pdf')]
        
        all_chunks_data = []
        for pdf_path in files_list:
            logger.debug("populate_pdfs: Processing PDF at filepath %s", pdf_path)
            
            # Chunk the PDF
            chunks = chunk_pdf_in_memory(pdf_path)
            
            # Process each chunk
            for chunk_name, chunk_content in chunks:
                chunk_text = extract_text(chunk_content)
                embedding = self.botservice.embed(texts=[chunk_text])[0]
                all_chunks_data.append((chunk_name, chunk_text, embedding))
        
        # Store all chunks in batches
        if all_chunks_data:
            self.storage.store_pdf_chunks(all_chunks_data)
            logger.info(f"populate_pdfs: Stored {len(all_chunks_data)} chunks from {len(files_list)} PDFs")
        else:
            logger.warning("populate_pdfs: No PDFs found in directory")

    def update_user(self, username: str, prompt: str, response: str):
        """
        Updates the user's chat history and potentially refines their personality blurb based on the latest interactions.

        Args:
            username (str): The username whose data is being updated.
            prompt (str): The user's latest input.
            response (str): The chatbot's response.
        """
        logger.info("chat: Inserting chat history to the database")

        user_message = ChatMessage(MessageRole.USER, content=prompt)
        bot_message = ChatMessage(MessageRole.ASSISTANT, content=response)
        self.chat_history.append_chat_history(username, [user_message, bot_message])
        current_blurb = self.chat_history.retrieve_personality(username)
        history = self.chat_history.retrieve_chat_history(username)
        recent = history[-BLURB_HISTORY_CONTEXT:] if len(history) > BLURB_HISTORY_CONTEXT else history

        # Format chat history into a readable string
        formatted_history = str(recent)

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

        new_blurb = self.botservice.chat(update_prompt, BLURB_MODEL_USE)
        self.chat_history.update_personality(username, Personality(new_blurb))

    def clear_history(self, username: str) -> None:
        """Clear the chat history for a given username."""
        self.chat_history.clear_chat_history(username)

    def add_feedback(self, username: str, feedback: str) -> None:
        """Add feedback for a user."""
        self.feedback_storage.add_feedback(username, feedback)

    def retrieve_all_feedback(self) -> list[dict[str, str]]:
        """Retrieve all stored feedback entries."""
        return self.feedback_storage.retrieve_all_feedback()

    def clear_feedback_storage(self) -> None:
        """Clear the feedback storage."""
        self.feedback_storage.clear_database()

    
    def get_storage_stats(self) -> dict:
        """
        Get statistics about the PDF storage.
        
        Returns:
            dict: Storage statistics including total chunks, etc.
        """
        return self.storage.get_stats()

    def test_pipeline(self, pdf_path: str, test_query: str, username: str = "test_user", usertype: str = "adult") -> str:
        """
        Test the full pipeline by adding a PDF and making a chat query.
        
        Args:
            pdf_path (str): Path to a PDF file to add to the system.
            test_query (str): Query to test the chat functionality.
            username (str): Username for the chat history (default: "test_user").
            usertype (str): Type of user for response formatting (default: "adult").
            
        Returns:
            str: The response from the chatbot.
        """
        logger.info(f"test_pipeline: Testing with PDF {pdf_path} and query '{test_query}'")
        
        # # Add the PDF to the system
        self.add_pdf(pdf_path)
        # Get storage stats after adding the PDF
        stats = self.get_storage_stats()
        logger.info(f"test_pipeline: Storage stats after adding PDF: {stats}")
        
        # Make a chat query
        response = self.chat(test_query, username, usertype)
        
        logger.info(f"test_pipeline: Received response: {response[:100]}...")
        return response


if __name__ == "__main__":
    import os
    import logging
    from openai import OpenAI
    from dotenv import load_dotenv

    from api.chatbot import Chatbot
    from api.botservice.gpt_botservice import GPTBotService
    from api.servicehandler.botservice_servicehandler import BotserviceServiceHandler
    from api.locationdatabase.sqlitelocationdatabase import SQLiteLocationDatabase
    from db_funcs.unified_pinecone_storage import UnifiedPineconeStorage
    from db_funcs.mongodb_chat_history_data_provider import MongoDBChatHistoryProvider
    from utils import setup_mongo_db
    from logger import setup_logger

    load_dotenv()

    # Running this setup in main.py will not correctly initialise settings, so the logger must be set up in here
    # NOTE: currently, the logger will always log to the file app.log even through multiple running processes
    setup_logger("app.log")
    logger = logging.getLogger(__name__)

    api_key = os.environ["OPENAI_API_KEY"]
    openai_client = OpenAI(api_key=api_key)
    logger.info("Connected to OpenAI")
    botservice = GPTBotService(openai_client)

    location_database = SQLiteLocationDatabase()
    location_database.initialize_database()
    location_database.create_snapshot()

    # MongoDB is still used for chat history
    mongo_db = setup_mongo_db()
    chat_history = MongoDBChatHistoryProvider(mongo_db)

    # Initialize unified Pinecone storage for PDFs and embeddings
    storage = UnifiedPineconeStorage()
    logger.info("Connected to Pinecone storage")

    service_handler = BotserviceServiceHandler(botservice, location_database)

    chatbot_obj = Chatbot(storage, chat_history, botservice, service_handler)
    
    pdf_path = 'autism_handbook.pdf'
    test_query ='whats autism'
    

        
    # Run the test pipeline
    response = chatbot_obj.test_pipeline(pdf_path, test_query)
    print(f"\nTest Query: {test_query}")
    print(f"\nChatbot Response:\n{response}")





