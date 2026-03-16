from config.settings import SETTING, LOG
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel


class DATABASE:
    _instance = None
    client = None

    def __new__(cls):
        if cls._instance is None:
            LOG.debug("Initializing DATABASE singleton")
            cls._instance = super(DATABASE, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._initialize_mongodb_client()
        self._ensure_vector_index()

    def _initialize_mongodb_client(self):
        if DATABASE.client is None:
            DATABASE.client = MongoClient(SETTING.MONGO_URI)
            LOG.info("MongoDB connected")

    def _ensure_vector_index(self):
        try:
            LOG.debug(
                f"Ensuring vector index for {SETTING.VECTOR_SEARCH.DB_NAME}.{SETTING.VECTOR_SEARCH.COLLECTION}"
            )

            db = DATABASE.client[SETTING.VECTOR_SEARCH.DB_NAME]
            collection = db[SETTING.VECTOR_SEARCH.COLLECTION]

            indexes = list(collection.list_search_indexes())

            if any(idx["name"] == SETTING.VECTOR_SEARCH.INDEX_NAME for idx in indexes):
                LOG.info("Vector index already exists")
                return

            LOG.info("Creating vector index...")


            index_model = SearchIndexModel(
                name=SETTING.VECTOR_SEARCH.INDEX_NAME,
                definition={
                    "mappings": {
                        "dynamic": True,
                        "fields": {
                            "embedding": {
                                "type": "knnVector",
                                "dimensions": 384,
                                "similarity": "cosine"
                            }
                        }
                    }
                }
            )

            collection.create_search_index(index_model)
            LOG.info("Vector index creation triggered")

        except Exception as e:
            LOG.error(f"Error ensuring vector index: {e}")
