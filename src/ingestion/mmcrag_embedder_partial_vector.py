from typing import Optional

from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import PdfFormatOption, DocumentConverter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama

from .mmcrag_ingestor import Ingestor
from ..utils.mmcrag_vlm import OllamaVLMService
from ..utils.mmcrag_config import config


class EmbedderPartialVector(Ingestor):

    def __init__(self, doc_name: str):
        super().__init__(doc_name)
        self._vlm_service = OllamaVLMService()


    ###Metodos para el enfoque de procesar las imagenes con u model vlm, el modelo retorna una descripcion detallada de la
    ###imagen en texto, que despues se vectoriza de manera estandar######################################################
    async def _generate_image_caption(self, image_path: str) -> str:
        """
        Genera la descripción técnica de la captura UI.
        Si hay un servicio VLM configurado se usa; si no, genera un fallback descriptivo.
        """
        if self._vlm_service:
            return await self._vlm_service.describe_ui(image_path)

        # Fallback por si ejecutas localmente sin VLM activo aún
        return f"Captura de interfaz de usuario extraída de {Path(image_path).name}"


    async def _create_vector_store(self) -> None:
        # Habilitar la extracción de imágenes en el pipeline de Docling
        # noinspection PyArgumentList
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = 2.0
        pipeline_options.generate_page_images = True
        pipeline_options.generate_picture_images = True
        pipeline_options.allow_external_plugins = True

        print("Extracting images with Docling")
        doc_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        # Procesar el documento
        conv_result = doc_converter.convert(str(self._document_path))
        docling_doc = conv_result.document

        # Carpetas para imágenes extraídas
        img_dir = self._db_path / config.IMAGES_FOLDER_NAME
        img_dir.mkdir(parents=True, exist_ok=True)

        documents = []

        print("Processing text (Markdown Chunks)")

        full_markdown_text = docling_doc.export_to_markdown()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.OVERLAP,
            separators=config.SEPARATORS
        )

        raw_chunks = text_splitter.split_text(full_markdown_text)

        print("Generating Chunks")
        for i, chunk_text in enumerate(raw_chunks):
            doc = Document(
                page_content=chunk_text,
                metadata={
                    "source": str(self._document_path),
                    "chunk_id": i,
                    "type": "text",
                    "image_path": "",
                    "has_image": False
                }
            )
            documents.append(doc)

        print(f"Generating and describing images")
        img_count = 0
        for element, _ in docling_doc.iterate_items():
            if hasattr(element, "image") and element.image:
                img_count += 1
                img_filename = f"ui_img_{img_count}.png"
                full_path = img_dir / img_filename

                # Guardar imagen físicamente
                element.image.pil_image.save(full_path)

                # Generar la descripción semántica mediante VLM
                caption = await self._generate_image_caption(str(full_path))

                # Crear Documento de LangChain para la IMAGEN
                img_doc = Document(
                    page_content=f"Captura de pantalla POS - Descripción UI: {caption}",
                    metadata={
                        "source": str(self._document_path),
                        "type": "image",
                        "image_path": str(full_path),
                        "has_image": True,
                        "image_id": img_count
                    }
                )
                documents.append(img_doc)

        print("Freeing up memory used by the vlm model")
        Ollama(model=config.VLM_MODEL, keep_alive=0)

        print("Generating vector store")

        self._vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self._embeddings_model,
            persist_directory=str(self._db_path)
        )

        print("Vector store created :D")


    def get_vector_store(self) -> Optional[Chroma]:
        try:
            self._db_path_vector_store_physical_validation()
            self._vector_store_physical_validations()

            self._vector_store = Chroma(
                persist_directory=str(self._db_path),
                embedding_function=self._embeddings_model
            )

            return self._vector_store
        except Exception as e:
            print(f"Error: An error occurred while generating/loading the vectorstore: {str(e)}")
            self._vector_store = None
            return None


    async def generate_vector_store(self) -> bool:
        try:
            self._db_path_vector_store_physical_validation()
            # noinspection PyBroadException
            try:
                self._vector_store_physical_validations()# si no existe lanza el except
                already_exists = True
            except Exception:
                already_exists = False
                await self._create_vector_store()

            if already_exists:
                raise RuntimeError("Vector already exists, delete it first to created it.")

            return True
        except Exception as e:
            print(f"Error: An error occurred while generating vectorstore: {str(e)}")
            return False



    def _db_path_vector_store_physical_validation(self) -> None:
        if not self._db_path.exists():
            raise RuntimeError("The path for the database does not exist.")


    def _vector_store_physical_validations(self) -> None:
        chroma_db_file = self._db_path / "chroma.sqlite3"

        if not chroma_db_file.exists():
            raise RuntimeError("Vector store does not exist. You must create it first.")