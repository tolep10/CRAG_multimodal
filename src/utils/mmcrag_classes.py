from typing import TypedDict, List, Optional, Any, Dict

from pydantic import BaseModel, Field


class DocumentStruct(TypedDict):
    """Estructura de un documento recuperado con sus metadatos visuales."""
    content: str
    image_path: str
    has_image: bool
    source: str
    type: str  # "text" o "image" (Opcional pero muy útil para filtrado)


class MMCRAGState(TypedDict):
    """Estado global que fluye a través de los nodos de LangGraph."""
    query: str  # Consulta actual (original o reescrita por rewrite_agent)
    original_query: str  # Pregunta inicial del usuario (preservada para trazabilidad)
    documents: List[DocumentStruct]  # Lista de documentos e imágenes recuperadas de ChromaDB
    is_relevant: Optional[bool]  # Flag de evaluación otorgado por visual_grader_agent
    generation: Optional[Dict[str, Any]]  # Respuesta estructurada redactada por generator_agent
    retry_count: int  # Contador para evitar bucles infinitos de reescritura
    error: Optional[str]  # Captura mensajes de fallo crítico


class MMCRAGResponseListDocument(BaseModel):
    """Clase que representa la informacion que retornan los metodos que retornan listas de DocumentStruct"""
    error: bool = Field(description="True si ocurrio un error en el proceso")
    documents: List[DocumentStruct] = Field(description="Lista de Documentos")
    cause: Optional[str] = Field(description="Causa del error, en caso de que haya ocurrido")

class MMCRAGResponseText(BaseModel):
    """Clase que representa la informacion que retornan los metodos que retornan respuestas de tipo str"""
    error: bool = Field(description="True si ocurrio un error en el proceso")
    cause: Optional[str] = Field(description="Causa del error, en caso de que haya ocurrido")
    response: Optional[str] = Field(description="Respuesta generada por el llm")

######### Clases que se usan como plantilla para respuestas de los LLM ################################################

class MMCRAGValidateRetrieverDocuments(BaseModel):
    """Clase que representa el formato de respuesta del modelo llm del grader"""
    argument: str = Field(description="Breve justificacion de la respuesta")
    is_relevant: bool = Field(description="La respuesta obtenida por el retriever satisface la consulta del usuario")

class MMCRAGLLMResponse(BaseModel):
    """Clase que representa el formato de respuesta del modelo llm del generator"""
    images: Optional[List[str]] = Field(description="Lista de images incluidas en la respuesta, si las hay, si no retorna []")
    content: str = Field(description="Respuesta a la consulta del usuario")

#######################################################################################################################
class MMCRAGFinalResponse(BaseModel):
    """Clase que representa la respuesta final que sera devuelta al grafo"""
    error: bool = Field(description="True si ocurrio un error en el proceso")
    cause: Optional[str] = Field(description="Causa del error, en caso de que haya ocurrido")
    response: Optional[MMCRAGLLMResponse] = Field(description="Respuesta generada por el llm")


