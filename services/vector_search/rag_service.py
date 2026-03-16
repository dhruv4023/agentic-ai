from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from services.vector_search.embedding_service import EmbeddingService
from config.settings import LOG, SETTING


PROMPT_TEMPLATE = """
You are a senior software engineer.

Use the following context to answer the question.

Context:
{context}

Question:
{question}

Answer with detailed explanation.
"""


class RagService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            LOG.info("Initializing RagService")
            cls._instance = super(RagService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        embedding_service = EmbeddingService()

        self.vectorstore = embedding_service.vector_store

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=SETTING.GEMINI_API_KEY,
            temperature=0.3,
        )

        self.prompt = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=["context", "question"],
        )

    # def _get_retriever(self, notebookId: int):
    #     return self.vectorstore.as_retriever(
    #         search_type="similarity",
    #         search_kwargs={
    #             "k": 5,
    #             "pre_filter": {"notebookId": notebookId},
    #         },
    #     )

    # def _build_chain(self, retriever):
    #     return RetrievalQA.from_chain_type(
    #         llm=self.llm,
    #         retriever=retriever,
    #         chain_type_kwargs={"prompt": self.prompt},
    #     )

    async def ask(self, question: str, notebookId: int) -> str:
        context = await self.get_context(question, notebookId, 0.60)

        if not context.strip():
            return "No relevant information found for this question."

        response = await self.llm.ainvoke(
            self.prompt.format(context=context, question=question)
        )

        return response.content


    async def get_context(self, question: str, notebookId: int, min_score: float = 0.25) -> str:
        docs_with_score = await self.vectorstore.asimilarity_search_with_score(
            question,
            k=5,
            pre_filter={"notebookId": notebookId},
        )

        filtered_docs = [
            doc.page_content
            for doc, score in docs_with_score
            if score > min_score
        ]

        return "\n\n".join(filtered_docs)[:3000]
