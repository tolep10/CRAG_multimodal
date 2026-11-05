import base64

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from .mmcrag_prompts import prompt_vlm
from .mmcrag_config import config


class OllamaVLMService:
    def __init__(self, model_name: str = config.VLM_MODEL):
        self._model_name = ChatOllama(model = model_name)



    async def describe_ui(self, image_path: str) -> str:
        """
        Envía la imagen del POS a Ollama para extraer la descripción visual y los textos.
        """
        try:
            image_base64 = self._encode_image(image_path)

            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": prompt_vlm
                     },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        },
                    },
                ]
            )

            response = await self._model_name.ainvoke([message])

            return response.text
        except Exception as e:
            print(f"ERROR processing image {image_path} with Ollama: {e}")
            return f"User interface capture in {image_path}"


    @staticmethod
    def _encode_image(image_path) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")