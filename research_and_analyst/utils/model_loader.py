import os
import sys
import asyncio
from dotenv import load_dotenv
from research_and_analyst.utils.config_loader import load_config
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_groq import GroqAI, GroqAIEmbeddings
from research_and_analyst.logger import GLOBAL_LOGGER as log
from research_and_analyst.exception.custom_exception import CustomException

class APIKeyManager:
    """ Loads and manages API keys from environment variables."""
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        
        self.api_keys = {
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
            # "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        }

        log.info("APIKeyManager initialized.")

        for key,value in self.api_keys.items():
            if value is None:
                log.error(f"Missing required API key: {key}")
                raise CustomException(f"Missing required API key: {key}")
            else:
                log.info(f"API key '{key}' loaded successfully.")
        
    def get(self, key: str) -> str:
        """ Retrieve an API key by name. """
        if key in self.api_keys:
            return self.api_keys[key]
        else:
            log.error(f"API key '{key}' not found.")
            raise CustomException(f"API key '{key}' not found.")

class ModelLoader:
    """ Initialize the ModelLoader and load configuration"""
    def __init__(self):
        try:
            self.api_key_manager = APIKeyManager()
            self.config = load_config()
            log.info("Models initialized successfully.")
        except Exception as e:
            log.error(f"CustomException during ModelLoader initialization: {e}")
            raise CustomException(f"Error initializing ModelLoader: {e}")
    
    def load_llm(self):
        """
        Loads the LLM Model
        
        Supported providers: google, openai, groq
        Returns:
            An instance of the loaded LLM model.
        """
        try:
            llm_block = self.config.get("llm", {})
            provider_key = os.getenv("LLM_PROVIDER", "openai").lower()

            if provider_key not in llm_block:
                log.error(f"LLM provider not found in configuration.", provider_key=provider_key)
                raise ValueError(f"LLM provider '{provider_key}' not found in configuration.")
            
            llm_config = llm_block[provider_key]
            provider = llm_config.get("provider")
            model_name = llm_config.get("model_name")
            temperature = llm_config.get("temperature", 0.2)
            max_tokens = llm_config.get("max_output_tokens", 2048)

            log.info(f"Loading LLM model", provider=provider, model_name=model_name)

            if provider == "google":
                llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature, max_output_tokens=max_tokens, api_key=self.api_key_manager.get("GOOGLE_API_KEY"))
            elif provider == "openai":
                llm = ChatOpenAI(model=model_name, temperature=temperature, max_tokens=max_tokens, api_key=self.api_key_manager.get("OPENAI_API_KEY"))
            elif provider == "groq":
                # llm = GroqAI(model=model_name, temperature=temperature, max_tokens=max_tokens, api_key=self.api_key_manager.get("GROQ_API_KEY"))
                pass
            else:
                log.error(f"Unsupported LLM provider: {provider}")
                raise ValueError(f"Unsupported LLM provider {provider}")
            
            log.info(f"LLM model loaded successfully", provider=provider, model_name=model_name)
            return llm
        except Exception as e:
            log.error("Error loading LLM", error = str(e))
            raise CustomException(f"Failed to load LLM model", sys)

    def load_embeddings(self):
        """ 
        Load and return a google generative embedding model
        
        Returns:
            An instance of the loaded embedding model."""
        try:
            model_name = self.config["embedding_model"]["model_name"]
            log.info(f"Loading embedding model", model_name=model_name)
            try:
                asyncio.get_running_loop()
                log.info("Event loop already running, using existing loop for async operations.")
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())


            embeddings = GoogleGenerativeAIEmbeddings(
                model=model_name, 
                api_key=self.api_key_manager.get("GOOGLE_API_KEY")
            )

            log.info(f"Embedding model loaded successfully", model_name=model_name)
            return embeddings
        except Exception as e:
            log.error("Error loading embedding model", error=str(e))
            raise CustomException(f"Failed to load embedding model: {e}", sys)
        

if __name__ == "__main__":
    try:
        loader = ModelLoader()

        embeddings = loader.load_embeddings()
        print(f"Embeddings model loaded: {embeddings}")
        result = embeddings.embed_query("What is the capital of France?")
        print(f"Embedding result: {result[:5]}...")  # Print only the first 5 dimensions for brevity

        llm = loader.load_llm()
        print(f"LLM loaded: {llm}")
        results = llm.invoke(["What is the capital of France?"])
        print(f"LLM response: {results.content}")

        log.info("ModelLoader test completed successfully.")
    except CustomException as e:
        log.error("Critical failure in ModelLoader test", error=str(e))

    

