from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import mmcrag_router
from .utils.mmcrag_config import config
app = FastAPI()

app.include_router(mmcrag_router, prefix='/api/mmcrag_d_t', tags=['mmcrag'])

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def health_check():
    return {'message': 'Bienvenido usuario, estamos listos para procesar tus consultas...'}