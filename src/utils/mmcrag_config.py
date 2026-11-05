import os
from typing import Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from pydantic import SecretStr

load_dotenv()

class Config:
    IMAGES_FOLDER_NAME = "extracted_images"
    BASE_PATH = "C:\\Users\\tolep\\Documents\\proyectos\\IA_projects\\langchain_langgraph_projects\\multimodal_RAG_for_technical_support\\"
    DOCS_DIR = BASE_PATH +"docs"
    DB_PATH = BASE_PATH + "data"
    IMG_DIR = BASE_PATH + DB_PATH + f"\\{IMAGES_FOLDER_NAME}"
    EMBEDDING_MODEL = "qwen3-embedding:4b"
    VLM_MODEL = "ministral-3:3b"
    URL_EMBEDDED = "http://localhost:11434/api/embed"
    DOCUMENT = "manual_pos-1.pdf"
    CHUNK_SIZE = 1000
    OVERLAP = 200
    SEPARATORS = ["\n## ", "\n### ", "\n\n", "\n", " "]
    GROQ_MINI = "openai/gpt-oss-20b"
    GROQ_MAX = "openai/gpt-oss-120b"
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_LLM: Optional[str] = os.getenv("GEMINI")
    llm_gemini: Optional[ChatGoogleGenerativeAI] = None
    llm_groq: Optional[ChatGroq] = None
    llm_groq_max: Optional[ChatGroq] = None
    MAX_RETRIES = 2
    origins = ["http://localhost:8000"]

    @classmethod
    def get_llm_groq(cls, max_groq: bool = False) -> Optional[ChatGroq]:
        try:
            if cls.GROQ_API_KEY:
                secret_groq = SecretStr(cls.GROQ_API_KEY)

                if max_groq:
                    if not cls.llm_groq_max:
                        cls.llm_groq_max = ChatGroq(api_key=secret_groq, model=cls.GROQ_MAX, temperature=0)

                    return cls.llm_groq_max

                else:
                    if not cls.llm_groq:
                        cls.llm_groq = ChatGroq(api_key=secret_groq, model=cls.GROQ_MINI, temperature=0)

                    return cls.llm_groq

            raise RuntimeError(
                f'{"No Groq API key" if not cls.GROQ_API_KEY else "Unknow error"}, unable to load Groq model {"MAX" if max_groq else "MIN"}')
        except Exception as e:
            print({str(e)})
            return None

    @classmethod
    def get_llm_gemini(cls) -> Optional[ChatGoogleGenerativeAI]:
        try:
            if cls.GEMINI_API_KEY:
                if not cls.llm_gemini:
                    cls.llm_gemini = ChatGoogleGenerativeAI(api_key=cls.GEMINI_API_KEY, model=cls.GEMINI_LLM,
                                                            temperature=0)

                return cls.llm_gemini

            raise RuntimeError('No Google API key provided')
        except Exception as e:
            print(f"No llm evaluator loaded: {str(e)}")
            return None



config = Config()