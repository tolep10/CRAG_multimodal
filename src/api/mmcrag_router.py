from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from .mmcrag_models import MMCRAGResponseDTO, MMCRAGRequestDTO
from .mmcrag_dependencies import get_mmcrag_service
from .mmcrag_service import MMCRAGService

mmcrag_router = APIRouter()

@mmcrag_router.post("/test", response_model=MMCRAGResponseDTO, status_code=HTTPStatus.OK)
async def test(question: MMCRAGRequestDTO, mmcrag_service: Annotated[MMCRAGService, Depends(get_mmcrag_service)]):
    mmcrag_response = await mmcrag_service.test_request(question)

    return mmcrag_response



@mmcrag_router.post("/", response_model=MMCRAGResponseDTO, status_code=HTTPStatus.OK)
async def request_mmcrag(question: MMCRAGRequestDTO,  mmcrag_service: Annotated[MMCRAGService, Depends(get_mmcrag_service)]):
    mmcrag_response = await mmcrag_service.launch_request(question)

    return mmcrag_response