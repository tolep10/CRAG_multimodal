import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from ..utils.mmcrag_config import config

class Ingestor(ABC):
    def __init__(self, doc_name: str):
        self._document_path = Path(config.DOCS_DIR) / doc_name
        self._vector_store = None
        self._embeddings_model = OllamaEmbeddings(model=config.EMBEDDING_MODEL)
        self._url_embedded = config.URL_EMBEDDED
        self._db_path = Path(config.DB_PATH)


    @abstractmethod
    async def _create_vector_store(self) -> None:
        ...

    @abstractmethod
    def get_vector_store(self) -> Optional[Chroma]:
        ...


    def _purge_db(self) -> None:
        if not self._db_path.exists():
            return

        for item in self._db_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(str(item))


    def rebuild_vector_store(self) -> Optional[Chroma]:
        self._vector_store = None
        self._purge_db()

        return self.get_vector_store()