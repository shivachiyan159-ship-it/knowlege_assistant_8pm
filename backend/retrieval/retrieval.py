

import sys

from backend.utils.config_loader import load_config
from backend.utils.model_loader import ModelLoader
from backend.logger import GLOBAL_LOGGER as log
from backend.exception.custom_exception import CustomException
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate
from backend.prompts.prompts import PROMPT_REGISTRY
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser


class ConversationalRAG:
    # attributes
    # methods
    # constriuctor
    def __init__(self):
        # build retrieval
        self.embed_model = ModelLoader().load_embedding()
        self.config = load_config()
        self.llm = self.__load_llm()
        self.retriever = self.__load_qdrant_retrievar()
        log.info("retriever craeetd successfully")

        # build prompt
        log.info("building lcel chain")
        self.chain = None
        if self.retriever is not None:
            self.__lcel_chain()
            log.info("completed lcel cjain")

    def __format_docs(self, docs):
        context = " ".join([doc.page_content for doc in docs])
        return context

    def __lcel_chain(self):
        try:
            # 1. rewrite user question with chathostory context
            context_question_prompt: ChatPromptTemplate = PROMPT_REGISTRY["contextualize_question"]

            question_rewriter = (
                {"input": itemgetter(
                    "input"), "chat_history": itemgetter("chat_history")}
                | context_question_prompt
                | self.llm
                | StrOutputParser()
            )

            retrived_context = question_rewriter | self.retriever | self.__format_docs

            # 2. Answer using retrieved context + question rewrite
            context_qa_prompt: ChatPromptTemplate = PROMPT_REGISTRY["context_qa"]

            self.chain = (
                {"context": retrived_context, "input": itemgetter("input")}
                | context_qa_prompt
                | self.llm
                | StrOutputParser()
            )

            log.info("LCEL graph or chain build successfully")

        except Exception as e:
            log.error(
                f"failed to vbuild LCEL chain in ConverstationalRAG {str(e)}")
            raise CustomException(
                f"failed to vbuild LCEL chain in ConverstationalRAG {str(e)}", sys)

    def __load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            if not llm:
                raise ValueError("LLM could not be found")

            log.info("LLM loaded successfully")
            return llm
        except Exception as e:
            log.error(f"failed to load llm {str(e)}")
            raise CustomException(f"failed to load llm {str(e)}", sys)

    def __load_qdrant_retrievar(self):
        try:
            vectorstore = QdrantVectorStore.from_existing_collection(
                embedding=self.embed_model,
                path="qdrantdb",
                collection_name="knowledge_assistant"
            )
            top_k = self.config["retriever"]["top_k"]
            retriever = vectorstore.as_retriever(search_args={"k": top_k})
            log.info("successfully created retriever")
            return retriever

        except Exception as e:
            log.error(f"failed to get retriever {str(e)}")
            raise CustomException(f"failed to get retriever {str(e)}", sys)

    def Chat(self, user_input, chat_history):
        try:
            if self.chain is None:
                raise ValueError("RAG chain not initialized")

            chat_history = chat_history or []
            payload = {"input": user_input, "chat_history": chat_history}

            answer = self.chain.invoke(payload)

            if not answer:
                log.warning(f"No answer generated {user_input}")
                return "No answer generated"

            log.info(
                f"chain invoked successfully and generated answer {user_input} {str(answer[:100])}")
            return answer

        except Exception as e:
            log.error(f"failed to invoke ConverstaionalRAG {str(e)}")
            raise ChatPromptTemplate(
                f"failed to invoke ConverstaionalRAG {str(e)}", sys)
