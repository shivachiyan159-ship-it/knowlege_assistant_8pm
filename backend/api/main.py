from typing import List
import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.params import Form
from backend.ingestion.document_ingestion import DocumentIngestion
from backend.logger import GLOBAL_LOGGER as log
from backend.utils.file_ops import FastAPIFileAdapter


load_dotenv()

FileUploadPath = os.getenv("File_Upload_Path")


app = FastAPI()


@app.get("/")
def greet():
    return "welcome to Conversational RAG"


@app.post("/chat/ingestion")
def document_ingestion(files: List[UploadFile] = File(...),
                       chunk_size=Form(1000),
                       chunk_overlap=Form(200)):
    try:
        log.info("document ingestion started")

        wrapped = [FastAPIFileAdapter(file)
                   for file in files]  # [obj1,obj2,obj3]
        docingestion = DocumentIngestion()
        docingestion.insertvectordb(
            wrapped, FileUploadPath, chunk_size, chunk_overlap)
        log.info("Document Ingestion Complted Sucessfully")
        return {"Response": "Document ingestion completed suceeffully"}

    except Exception as e:
        log.error(f"Documnet ingestion failed {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"indexing failed {str(e)}")
