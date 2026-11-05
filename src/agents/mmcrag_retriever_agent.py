from langchain_core.documents import Document

from ..ingestion.mmcrag_embedder_partial_vector import EmbedderPartialVector
from ..utils.mmcrag_classes import DocumentStruct, MMCRAGResponseListDocument
from ..utils.mmcrag_config  import config

class RetrieverAgent:
    def __init__(self, doc_name: str = config.DOCUMENT):
        self._retriever = None
        self._embedder = EmbedderPartialVector(doc_name)



    def _build_retriever(self) -> None:
        vectorstore = self._embedder.get_vector_store()

        if not vectorstore:
            raise RuntimeError("Fail retrieving the vectorstore")

        self._retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 10
            }
        )



    async def search_in_vectorstore(self, query: str) -> MMCRAGResponseListDocument:
        try:

            if not self._retriever:
                self._build_retriever()


            response = await self._retriever.ainvoke(query)

            documents = [self._map_langchain_doc_to_state(doc) for doc in response]

            return MMCRAGResponseListDocument(error=False, documents=documents, cause = None)

        except Exception as e:
            print(f"ERROR: An error occurred while executing the query. {str(e)}")
            return MMCRAGResponseListDocument(error=True, documents=[], cause = str(e))




    @staticmethod
    def _map_langchain_doc_to_state(doc: Document) -> DocumentStruct:
        # Extraemos los metadatos construidos deterministamente en Colab
        metadata = doc.metadata
        is_image = metadata.get("has_image", False)
        img_path = metadata.get("image_path", "")


        # Mapeo exacto hacia tu estructura DocumentState
        doc_state_item: DocumentStruct = {
            "content": doc.page_content,  # Texto del fragmento o el contexto/caption de la interfaz
            #"image_path": validated_img_path,
            "image_path": img_path,
            "has_image": is_image,
            "source": metadata.get("source", "Unknown"),
            "type": metadata.get("type", "text")  # "text" o "image"
        }

        return doc_state_item
