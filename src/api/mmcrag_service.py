import asyncio
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from langgraph.graph.state import CompiledStateGraph

from .mmcrag_models import MMCRAGResponseDTO, MMCRAGRequestDTO
from ..mmcrag_graph import MMCRAGGraph


class MMCRAGService(ABC):
    def __init__(self, graph: MMCRAGGraph):
        self._graph =  graph


    @abstractmethod
    def get_workflow(self) -> CompiledStateGraph:
        ...

    @abstractmethod
    async def launch_request(self, question: MMCRAGRequestDTO) -> MMCRAGResponseDTO:
        ...

    @abstractmethod
    async def test_request(self, question: MMCRAGRequestDTO) -> MMCRAGResponseDTO:
        ...



class MMCRAGServiceImpl(MMCRAGService):
    def get_workflow(self) -> CompiledStateGraph:
        if not self._graph:
            raise RuntimeError("Error to get workflow, graph injection not working")

        app_graph = self._graph.get_grap_workflow()

        if not app_graph:
            raise RuntimeError("Error to get workflow, compiled graph is None")

        return app_graph



    async def launch_request(self, question: MMCRAGRequestDTO) -> MMCRAGResponseDTO:
        try:
            app_graph: Optional[CompiledStateGraph] = self.get_workflow()

            if not app_graph:
                raise RuntimeError("Error to get workflow")

            initial_state = {
                "query": question.query,
                "retry_count": 1,
            }

            final_state: Dict[str, Any] = await app_graph.ainvoke(initial_state)
            generation = final_state.get("generation", {})

            if not generation:
                raise RuntimeError("Error to get workflow")

            return MMCRAGResponseDTO(images=generation.get("images"), content=generation.get("content"), error=False, http_status_code=200, cause=None)
        except Exception as e:
            return MMCRAGResponseDTO(images=[], content="", error=True, http_status_code=500, cause=str(e))


    async def test_request(self, question: MMCRAGRequestDTO) -> MMCRAGResponseDTO:
        return await asyncio.to_thread(MMCRAGServiceImpl._get_mocks)


    @staticmethod
    def _get_mocks() -> MMCRAGResponseDTO:
        time.sleep(1)

        return MMCRAGResponseDTO(images=["data/extracted_images/ui_img_11.png","data/extracted_images/ui_img_12.png"],
            content="""
            Para cerrar la caja sigue estos pasos sencillos:

        1. **Abre la ventana de cierre de caja**. Busca la opción “Cierre de Caja” en el menú del POS y selecciónala.
        2. **Compara los datos**. En la ventana aparecerán los valores teóricos (lo que el sistema espera) y tú deberás ingresar los valores reales que tienes en la caja (efectivo, tarjetas, cheques, etc.).
        3. **Presiona el botón “Cerrar Caja”**. Está centrado en la pantalla y tiene el ícono de una persona con una cruz.
        4. **Revisa el reporte**. Después de cerrar, el sistema mostrará un reporte con la información de los movimientos realizados.

        Con estos pasos la caja quedará cerrada y tendrás un informe para tus registros.""",
            error=False,
            cause=None,
            http_status_code=200,)

