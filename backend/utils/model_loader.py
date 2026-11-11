
from dotenv import load_dotenv
from backend.logger import GLOBAL_LOGGER as log
from backend.utils.config_loader import load_config
from langchain_huggingface import HuggingFaceEmbeddings
from backend.exception.custom_exception import CustomException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import os
import sys


class ModelLoader:
    # attributes
    # methods
    # special member method
    def __init__(self):
        load_dotenv()  # for loading env variables in python env
        log.info("loading config")
        self.config = load_config()
        log.info(self.config)

    def load_embedding(self):
        try:
            embed_model_name = self.config["embedding_model"]["model_name"]
            log.info("loadedd embedding model name from config",
                     model=embed_model_name)

            return HuggingFaceEmbeddings(model_name=embed_model_name)

        except Exception as e:
            log.error("Error loading embeding model", error=str(e))
            raise CustomException("Error loading embeding model", sys)

    def load_llm(self):
        try:
            llm_block = self.config["llm"]
            provider_key = os.getenv("LLM_PROVIDER")

            if provider_key not in llm_block:
                log.error(f"LLM provider not found in config {provider_key}")
                return ValueError(f"LLM provider {provider_key} not found in config")

            llm_config = llm_block[provider_key]
            model_name = llm_config.get("model_name", "")
            temprature = llm_config.get("temprature")
            max_tokens = llm_config.get("max_output_tokens")
            provider = llm_config.get("provider")

            log.info(
                f"loading llm {provider_key} and  model name is {model_name}")

            if provider == "google":
                return ChatGoogleGenerativeAI(model=model_name, temprature=temprature, max_tokens=max_tokens)
            elif provider == "groq":
                return ChatGroq(model=model_name, max_tokens=max_tokens, temperature=temprature)
            else:
                return ChatOpenAI(model=model_name, max_tokens=max_tokens, temperature=temprature)

        except Exception as e:
            log.error(f"Error loading llm {str(e)}")
            raise CustomException(f"Error loading llm {str(e)}", sys)


if __name__ == "__main__":
    loader = ModelLoader()
    # test embedding
    # embedding = loader.load_embedding()
    # embed_result = embedding.embed_query("hi how are you")
    # print(embed_result)

    # test llm
    llm = loader.load_llm()
    response = llm.invoke("what is generative ai ?")
    print(f"LLM Result: {response.content}")
