import chromadb
from chromadb.config import Settings
from datetime import datetime
from config.settings import CHROMA_DB_PATH, COLLECTION_NAME
from utils.logger import get_logger

logger = get_logger(__name__)

class ResearchMemory:
    """
    Manages long-term memory for the research crew using ChromaDB.
    Stores past research results so agents can reference previous work.

    Think of this as the crew's shared notebook — any agent can
    write to it or search through it at any time.
    """

    def __init__(self):
        """Initializes ChromaDB client and get/create the collection."""
        try:
            #create persistent client, data survive between runs
            self.client = chromadb.PersistentClient(
                path = CHROMA_DB_PATH,
                settings = Settings(anonymized_telemetry=False)
            )

            #get or create research collection
            #a collection is like a table in regular database
            self.collection = self.client.get_or_create_collection(
                name = COLLECTION_NAME,
                metadata = {"description": "Research crew long-term memory"}
            )

            logger.info(f"ChromaDB initialized at: {CHROMA_DB_PATH}")
            logger.info(f"Collection '{COLLECTION_NAME}' ready - {self.collection.count()} entries stored")

        except Exception as e:
            logger.error(f"Failed to initialized ChromaDB: {e}")
            raise

    def store_research(self, topic:str, content:str, doc_type:str = "research") -> str:
        """
        Stores research content in the vector database.

        Args:
            topic: The research topic
            content: The content to store
            doc_type: Type of document ('research', 'analysis', 'report')

        Returns:
            str: The document ID assigned to this entry
        """
        #generate unique ID using topic + timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_id = f"{doc_type}_{topic[:30].replace(' ','_')}_{timestamp}"

        try:
            self.collection.add(
                documents = [content],
                metadatas = [{
                    "topic": topic,
                    "type": doc_type,
                    "timestamp": timestamp,
                    "word_count": str(len(content.split())),
                }],
                ids = [doc_id]
            )
            logger.info(f"Stored {doc_type} for topic '{topic}' | ID: {doc_id}")
            return doc_id

        except Exception as e:
            logger.error(f"Failed to store research: {e}")
            raise

    def search_memory(self, query:str, n_results: int=3, doc_type:str = None) -> list[dict]:
        """
        Searches memory for content similar to the query.

        Args:
            query: What to search for
            n_results: How many results to return
            doc_type: Optional filter by document type

        Returns:
            list of dicts with 'content', 'topic', 'type', 'timestamp'
        """
        try:
            where_filter = {"type": doc_type} if doc_type else None
            results = self.collection.query(
                query_texts = [query],
                n_results = min(n_results, self.collection.count() or 1),
                where = where_filter
            )

            #format results into readable dicts
            formatted =[]
            if results["documents"] and results ["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted.append({
                        "content": doc,
                        "topic": results["metadatas"][0][i].get("topic"),
                        "type": results["metadatas"][0][i].get("type"),
                        "timestamp": results["metadatas"][0][i].get("timestamp"),
                        "relevance_scope": round(1 - results["distances"][0][i], 3)
                    })
            logger.info(f"Memory search for '{query}' returned {len(formatted)} results")
            return formatted

        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []

    def get_related_research(self, topic: str) -> str:
        """
        Convenience method - returns a formatted string or related past research for injection into agent context.

        Args:
            topic: Current research topic

        Returns:
        str: Formatted past research context, or empty string if none
        """
        results = self.search_memory(query = topic, n_results = 3)

        if not results:
            return ""
        context = "RELEVANT PAST RESEARCH FROM MEMORY:\n"
        context += "=" * 40 + "\n\n"

        for i, result in enumerate (results, 1):
            context += (
                f"{i}. Topic: {result['topic']}\n"
                f"  Type: {result['type']}\n"
                f"  Date: {result['timestamp']}\n"
                f"  Relevance: {result['relevance_scope']}\n"
                f"  Preview: {result['content'][:200]}...\n\n"
            )
        return context

    def list_all_topics(self) -> list[str]:
        """Returns a list of all topics stored in memory."""
        try:
            results = self.collection.get()
            topics = list(set(
                meta.get("topic", "Unknown")
                for meta in results["metadatas"]
            ))
            return sorted(topics)

        except Exception as e:
            logger.error(f"Failed to liat topics: {e}")
            return []

    def clear_memory(self) -> None:
        """Clear all stored research. Use with Caution"""
        try:
            self.client.delete_collection(COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name = COLLECTION_NAME
            )
            logger.warning("Memory cleared - all research history deleted")

        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            raise

#test module
if __name__ == "__main__":
    print("Testing ChromaDB memory...")
    memory = ResearchMemory()

    #sorting test
    doc_id = memory.store_research(
        topic="AI in healthcare",
        content="AI is transforming healthcare through improved diagnostics, "
                "drug discovery, and patient monitoring. Studies show AI can "
                "reduce diagnostic errors by up to 30% in radiology.",
        doc_type="research"
    )
    print(f"Stored document: {doc_id}")

    #test searching
    results = memory.search_memory("machine learning medicine")
    print(f"\nSearch results for 'machine learning medicine':")
    for r in results:
        print(f"Topic: {r['topic']}")
        print(f"Relevance: {r['relevance_scope']}")
        print(f"Preview: {r['content'][:100]}...")

    #test listing topics
    topics = memory.list_all_topics()
    print(f"\nStored Topic list: {topics}")

    print("\n> ChromaDB memory working correctly <")



