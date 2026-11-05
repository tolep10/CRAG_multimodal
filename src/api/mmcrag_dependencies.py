from typing import Annotated

from .mmcrag_service import MMCRAGService, MMCRAGServiceImpl
from fastapi.params import Depends

from ..mmcrag_graph import MMCRAGGraph


def get_graph() -> MMCRAGGraph:
    return MMCRAGGraph()

def get_mmcrag_service(graph: Annotated[MMCRAGGraph, Depends(get_graph)]) -> MMCRAGService:
    return MMCRAGServiceImpl(graph)