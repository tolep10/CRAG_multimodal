
from langgraph.constants import END, START
from langgraph.graph.state import CompiledStateGraph, StateGraph
from .agents import RetrieverAgent, RewriterAgent, GeneratorAgent, GraderAgent
from .utils.mmcrag_classes import *
from .utils.mmcrag_config import config

class MMCRAGGraph:
    def __init__(self):
        self._graph: Optional[CompiledStateGraph] = None
        self._retriever: RetrieverAgent = RetrieverAgent()
        self._rewriter: RewriterAgent = RewriterAgent()
        self._grader: GraderAgent = GraderAgent()
        self._generator: GeneratorAgent = GeneratorAgent()


    async def retriever_node(self, state: MMCRAGState) -> Dict[str, Any]:
        """Nodo encargado de obtener documentos del la vs"""

        try:
            query: str = state.get("query")

            retriever_resp: MMCRAGResponseListDocument = await self._retriever.search_in_vectorstore(query)

            if retriever_resp.error:
                raise RuntimeError(retriever_resp.cause)

            return {
                "documents": retriever_resp.documents,
            }


        except Exception as e:
            print(f"Error en el nodo retrieval: {str(e)}")
            return {
                "error": str(e),
            }


    async def grader_node(self, state: MMCRAGState):
        """Nodo encargado de llamar al grader para validar los documentos que devolvio el retriever"""
        try:
            documents: List[DocumentStruct] = state.get("documents")
            query: str = state.get("query")

            grader_resp: MMCRAGResponseListDocument = await self._grader.validating_retriever_documents(documents, query)

            if grader_resp.error:
                raise RuntimeError(grader_resp.cause)

            if grader_resp.documents:
                return {
                    "is_relevant": True,
                    "documents": grader_resp.documents,
                }

            return {
                "is_relevant": False,
                "documents": [],
            }
        except Exception as e:
            print(f"Error en el nodo grader: {str(e)}")
            return {
                "error": str(e),
            }


    async def rewriter_node(self, state: MMCRAGState):
        """Nodo encargado de reescribir la query si el grader o el retriever no devuelven documentos"""
        try:
            current_retry = state.get("retry_count", 1)
            query = state.get("query")
            rw_resp : MMCRAGResponseText = await self._rewriter.get_rewrite_query(query)

            if rw_resp.error:
                raise RuntimeError(rw_resp.cause)

            print(f"Rewriter {rw_resp.response if rw_resp.response else ''}")

            return {
                "query": rw_resp.response,
                "retry_count": current_retry + 1,
            }

        except Exception as e:
            print(f"Error en el nodo rewriter: {str(e)}")
            return {
                "error": str(e),
            }

    async def generator_node(self, state: MMCRAGState):
        """Nodo encargado de generar la respuesta final"""
        try:
            documents: List[DocumentStruct] = state.get("documents", [])

            if not documents:
                return {
                    "generation": {"images": [], "content": ""}
                }

            query = state.get("query")

            gene_resp: MMCRAGFinalResponse = await self._generator.get_final_response(documents, query)

            if gene_resp.error or not gene_resp.response:
                raise RuntimeError(gene_resp.cause or "La respuesta no se puede generar")


            return {
                "generation": MMCRAGGraph._process_final_response(gene_resp),
            }
        except Exception as e:
            print(f"Error en el nodo generador: {str(e)}")
            return {
                "error": str(e),
            }


    def build(self) -> None:
        """Ensambla los nodos, bordes y bordes condicionales en el StateGraph."""
        # noinspection PyTypeChecker
        builder = StateGraph(MMCRAGState)
        # noinspection PyTypeChecker
        builder.add_node("retriever", self.retriever_node)
        # noinspection PyTypeChecker
        builder.add_node("grader", self.grader_node)
        # noinspection PyTypeChecker
        builder.add_node("rewriter", self.rewriter_node)
        # noinspection PyTypeChecker
        builder.add_node("generator", self.generator_node)

        builder.add_edge(START, "retriever")

        builder.add_conditional_edges(
            "retriever",
            MMCRAGGraph._router_after_retriever,
            {
                "grader": "grader",
                "rewriter": "rewriter",
                "generator": "generator",
                END: END,
            },
        )

        builder.add_conditional_edges(
            "grader",
            MMCRAGGraph._router_after_grader,
            {
                "generator": "generator",
                "rewriter": "rewriter",
                END: END,
            },
        )

        builder.add_conditional_edges(
            "rewriter",
            MMCRAGGraph._router_after_rewriter,
            {
                "retriever": "retriever",
                END: END,
            }
        )


        builder.add_edge("generator", END)

        # noinspection PyTypeChecker
        self._graph = builder.compile()


    def get_grap_workflow(self) -> Optional[CompiledStateGraph]:
        try:
            if not self._graph:
                self.build()

            return self._graph
        except Exception as e:
            print(f"Error to build graph: {str(e)}")
            return None


    @staticmethod
    def _router_after_retriever(state: MMCRAGState) -> str:
        if state.get("error"):
            return END

        if state.get("documents"):
            return "grader"

        return MMCRAGGraph._retry(state)


    @staticmethod
    def _router_after_grader(state: MMCRAGState) -> str:
        if state.get("error"):
            return END

        if state["is_relevant"]:
            return "generator"


        return MMCRAGGraph._retry(state)


    @staticmethod
    def _router_after_rewriter(state: MMCRAGState) -> str:
        if state.get("error"):
            return END

        return "retriever"


    @staticmethod
    def _retry(state: MMCRAGState) -> str:
        tries = state.get("retry_count", 1)

        if tries >= config.MAX_RETRIES:
            return "generator"

        return "rewriter"



    @staticmethod
    def _process_final_response(response: MMCRAGFinalResponse) -> Dict[str, Any]:
        llm_response = response.response

        if llm_response:
            return {
                "images": llm_response.images,
                "content": llm_response.content,
            }

        return {"images": [], "content": ""}

