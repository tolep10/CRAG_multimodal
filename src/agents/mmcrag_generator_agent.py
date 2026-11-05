from typing import List

from langchain_core.prompts import ChatPromptTemplate

from ..utils.mmcrag_classes import DocumentStruct
from ..utils.mmcrag_config import config
from ..utils.mmcrag_classes import MMCRAGFinalResponse, MMCRAGLLMResponse
from ..utils.mmcrag_prompts import generator_prompt

class GeneratorAgent:
    def __init__(self):
        self._llm_generator = config.get_llm_groq(True)


    async def get_final_response(self, documents: List[DocumentStruct], query: str) -> MMCRAGFinalResponse:
        try:
            if not self._llm_generator:
                raise RuntimeError("Impossible to get LLM generator")

            full_content = GeneratorAgent._get_full_content(documents)

            cgenerator_prompt = ChatPromptTemplate.from_messages([
                ("system", generator_prompt),
                ("human", "{context}\n\nCONSULTA DEL USUARIO:\n{query}")
            ])

            structured_model = self._llm_generator.with_structured_output(MMCRAGLLMResponse)
            generator_chain = cgenerator_prompt | structured_model

            response: MMCRAGLLMResponse = await generator_chain.ainvoke({"query": query, "context": full_content})

            return MMCRAGFinalResponse(error=False, cause=None, response=response)

        except Exception as e:
            print(f"Error to generate final answer: {e}")
            return MMCRAGFinalResponse(error=True, cause=str(e), response=None)



    @staticmethod
    def _get_full_content(documents: List[DocumentStruct]) -> str:
        full_content_list: List[str] = []

        for document in documents:
            content_from = document.get("type", "Unknown")
            content = document.get("content", "")
            content_image = None

            if document.get("has_image"):
                path_image = document.get("image_path")
                content_image = f"- IMAGEN PATH: {path_image}" if path_image else ""

            source = document.get("source", "")


            full_content_list.append(f"""
                    METADATOS:
                    - FUENTE: {source}
                    - ORIGEN: {content_from}
                    {content_image if content_image else ''}
                    - CONTENIDO:
                    {content}
                    """)

        return "".join(full_content_list)