from pathlib import Path
from typing import Iterable, List
from backend.logger import GLOBAL_LOGGER as log
from backend.exception.custom_exception import CustomException
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
import re
import uuid
import sys


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def save_uplaod_files(uploadfiles: Iterable, targetdir: Path):
    try:
        # converting string to Path
        targetdir = Path(targetdir)
        targetdir.mkdir(exist_ok=True)

        saved: List[Path] = []

        for uf in uploadfiles:
            name = getattr(uf, "name", "file1.pdf")  # pythontutorial.pdf
            ext = Path(name).suffix.lower()
            if ext not in SUPPORTED_EXTENSIONS:
                log.warning(f"unsupported file {name}")
                continue

            # python_tutorial.pdf
            safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_',
                               Path(name).stem).lower()

            file_name = f"{safe_name}_{uuid.uuid4().hex[:6]}{ext}"

            out = targetdir/file_name

            with open(out, "wb") as f:
                if hasattr(uf, "read"):
                    f.write(uf.read())
                else:
                    f.write(uf.getbuffer())

            saved.append(out)
        return saved

    except Exception as e:
        log.error("failed to save upload file",
                  error=str(e), dir=str(targetdir))
        raise CustomException(
            f"failed to save upload file {str(e)} and filepath: {str(targetdir)}", sys)


def read_documents(paths: Iterable[Path]):
    """Load docs using appropriate loader based on extension
        blah blah blah
    """
    docs: List[any] = []
    try:
        for p in paths:
            ext = p.suffix.lower()
            if ext == ".pdf":
                # Document(pagecontent, metadata)
                loader = PyPDFLoader(str(p))
            elif ext == ".docx":
                loader = Docx2txtLoader(str(p))
            elif ext == ".txt":
                loader = TextLoader(str(p))
            else:
                log.warning("unsupported extension", path=str(p))
            # pdf file content  10 items+5 items+7 items
            docs.append(loader.load())
            log.info("Documents successfully loaded", count=len(docs))

        return docs

    except Exception as e:
        log.error("failed loading docuemnst", error=str(e))
        raise CustomException("Error loading documents")


class FastAPIFileAdapter:
    def __init__(self, uf):
        self.uf = uf
        self.name = uf.name

    def getbuffer(self):
        self.uf.file.seek(0)
        return self.uf.file.read()
