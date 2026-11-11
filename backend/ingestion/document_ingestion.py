import sys

from backend.utils.model_loader import ModelLoader
from backend.utils.config_loader import load_config
from backend.utils.file_ops import save_uplaod_files, read_documents
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.logger import GLOBAL_LOGGER as log
from backend.exception.custom_exception import CustomException
from langchain_qdrant import QdrantVectorStore


class DocumentIngestion:
    # attributes
    # methods
    # constrcutir
    def __init__(self):
        self.model_loader = ModelLoader()
        self.config = load_config()

    def __splitdocuemnts(self, docs, chunksize=1000, chunkoverlap=200):
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunksize,
                chunk_overlap=chunkoverlap,
                separators=["/n/n", "/n", " "]
            )
            chunks = splitter.split_documents(docs)
            log.info("Document split completed")
            return chunks
        except Exception as e:
            log.error(f"failed chunking {str(e)}")
            raise CustomException(f"failed chunking {str(e)}", sys)

    def __storevectordb(self, chunks):
        try:
            embed_model = self.model_loader.load_embedding()
            QdrantVectorStore.from_documents(
                documents=chunks,
                embedding=embed_model,
                path="qdrantdb",
                collection_name="knowledge_assistant"
            )
            log.info("stored vectors into vectordb")

        except Exception as e:
            log.error(f"failed storing vector db: {str(e)}")
            raise CustomException(f"failed storing vector db: {str(e)}", sys)

    def insertvectordb(self, uploadfiles, targetpath, chunksize, chunkoverlap):
        try:
            # read documents
            paths = save_uplaod_files(uploadfiles, targetpath)
            docs = read_documents(paths)
            # convert chunks
            chunks = self.__splitdocuemnts(docs, chunksize, chunkoverlap)
            # generate embeddings
            # store embeddings into vectordb
            self.__storevectordb(chunks)
        except Exception as e:
            log.error(f"failed insertvectordb method: {str(e)}")
            raise CustomException(
                f"failed insertvectordb method: {str(e)}", sys)
