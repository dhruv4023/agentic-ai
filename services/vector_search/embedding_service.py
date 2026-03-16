from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from config.settings import SETTING, LOG
from config.database import DATABASE

MONGO_URI = SETTING.MONGO_URI


class EmbeddingService:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            LOG.info("Initializing EmbeddingService")
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        db = DATABASE().client[SETTING.VECTOR_SEARCH.DB_NAME]
        collection = db[SETTING.VECTOR_SEARCH.COLLECTION]

        self.vector_store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embedding_model,
            index_name=SETTING.VECTOR_SEARCH.INDEX_NAME
        )

        LOG.info(
            f"EmbeddingService initialized with db: {SETTING.VECTOR_SEARCH.DB_NAME}, "
            f"collection: {SETTING.VECTOR_SEARCH.COLLECTION}, "
            f"index: {SETTING.VECTOR_SEARCH.INDEX_NAME}"
        )

    def generate_and_store(self, text: str, metadata: dict):
        note_id = metadata["noteId"]

        try:
            self.vector_store.delete(filter={"noteId": note_id})
        except Exception:
            pass  

        self.vector_store.add_texts(
            texts=[text],
            metadatas=[metadata]
        )

        return True

    async def search_similar_notes(self, query: str, k: int = 3):
        docs = self.vector_store.similarity_search(query, k=k)
        results = []
        for doc in docs:
            results.append(doc.page_content)

        return results
