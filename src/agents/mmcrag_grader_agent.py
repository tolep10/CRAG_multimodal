from typing import List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate

from ..utils.mmcrag_config import config
from ..utils.mmcrag_prompts import relevance_prompt
from ..utils.mmcrag_classes import MMCRAGResponseListDocument, DocumentStruct, MMCRAGValidateRetrieverDocuments


class GraderAgent:
    def __init__(self):
        self._llm_grader_aux = config.get_llm_groq(True)
        self._llm_grader = config.get_llm_gemini()


    async def validating_retriever_documents(self, documents: List[DocumentStruct], query: str) -> MMCRAGResponseListDocument:
        try:
            if not self._llm_grader and not self._llm_grader_aux:
                raise RuntimeError("Unable to get llm grader")


            grader_prompt = ChatPromptTemplate.from_messages([
                ("system", relevance_prompt),
                ("human", "{document}\n\nCONSULTA DEL USUARIO:\n{query}")
            ])

            clean_documents = [GraderAgent._clean_document(document) for document in documents]

            inputs = [
                {
                    "document": GraderAgent._processing_document(doc, index),
                    "query": query
                }
                for index, doc in enumerate(clean_documents)
            ]


            structured_model = self._llm_grader.with_structured_output(MMCRAGValidateRetrieverDocuments)

            # noinspection PyBroadException
            try:
                results = await GraderAgent._invoke_request(grader_prompt, inputs, structured_model)
            except Exception:
                structured_model = self._llm_grader_aux.with_structured_output(MMCRAGValidateRetrieverDocuments)
                results = await GraderAgent._invoke_request(grader_prompt, inputs, structured_model)


            relevant_docs: List[DocumentStruct] = []

            for doc, result in zip(clean_documents, results):
                if result.is_relevant:
                    relevant_docs.append(doc)

            return MMCRAGResponseListDocument(error=False, documents=relevant_docs, cause=None)
        
        except Exception as e:
            print(f"Error during to validate documents: {str(e)}")
            return MMCRAGResponseListDocument(error=True, documents=[], cause=str(e))



    @staticmethod
    async def _invoke_request(grader_prompt: ChatPromptTemplate, inputs: List[Dict[str, Any]], structured_model) -> List[MMCRAGValidateRetrieverDocuments]:
        grader_chain = grader_prompt | structured_model

        results: List[MMCRAGValidateRetrieverDocuments] = await grader_chain.abatch(inputs)

        return results


    @staticmethod
    def _clean_document(document: DocumentStruct) -> DocumentStruct:
        r_type = document.get("type", "Unknown")
        content = document.get("content", "")

        if r_type == "text":
            content = content.strip().replace("<!-- image -->", "")
            document["content"] = content

        return document


    @staticmethod
    def _processing_document(document: DocumentStruct, index: int = 0) -> str:
        content_from = document.get("type", "Unknown")
        content = document.get("content", "")
        content_image = None

        if document.get("has_image"):
            path_image = document.get("image_path")
            content_image = f"- IMAGEN: {path_image}" if path_image else ""


        source = document.get("source", "")

        header = f"--- DOCUMENTO {index} ---" if index > 0 else "--- DOCUMENTO ---"

        return f""" {header}
        METADATOS:
        - FUENTE: {source}
        - ORIGEN: {content_from}
        {content_image if content_image else ''}
        - CONTENIDO:
        {content}
        """
