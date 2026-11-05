from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable

from ..utils.mmcrag_config import config
from ..utils.mmcrag_classes import MMCRAGResponseText
from ..utils.mmcrag_prompts import rewrite_query_prompt

class RewriterAgent:
    def __init__(self):
        self._llm_rewriter = config.get_llm_groq()


    async def get_rewrite_query(self, query: str) -> MMCRAGResponseText:
        try:
            if not self._llm_rewriter:
                raise RuntimeError("Unable to get llm to generate the rewrite query")

            rewriter_prompt = ChatPromptTemplate.from_messages([
                ("system", rewrite_query_prompt),
                ("human", "CONSULTA DEL USUARIO: \n{query}")
            ])

            chain: RunnableSerializable = rewriter_prompt | self._llm_rewriter

            raw_response: AIMessage = await chain.ainvoke({"query": query})

            rewrite_query = raw_response.text

            return MMCRAGResponseText(error=False, response=rewrite_query, cause=None)

        except Exception as e:
            print(f"Error too get rewrite query: {str(e)}")
            return MMCRAGResponseText(error=True, cause=str(e), response=None)




