import chromadb
import hishel


controller = hishel.Controller(force_cache=True)
storage = hishel.FileStorage(
    ttl=7 * 60 * 60 * 24,  # Cache for 7 days
)
http_client = hishel.CacheClient(storage=storage, controller=controller)

chromadb_client = chromadb.PersistentClient()

organizations_collection = chromadb_client.get_or_create_collection(
    name="organizations"
)
memberships_collection = chromadb_client.get_or_create_collection(name="memberships")
persons_collection = chromadb_client.get_or_create_collection(name="persons")


# let's set up the hishel cache client, so that we can use it as a dependency in our endpoints
async def http_client_factory():
    """Factory function to create an HTTP client with caching."""
    return http_client


# This function can be used as a dependency in FastAPI endpoints
async def chromadb_persons_collection():
    """Factory function to create a ChromaDB client."""
    return persons_collection


# This function can be used as a dependency in FastAPI endpoints
async def chromadb_organizations_collection():
    """Factory function to create a ChromaDB client."""
    return organizations_collection


# This function can be used as a dependency in FastAPI endpoints
async def chromadb_memberships_collection():
    """Factory function to create a ChromaDB client."""
    return memberships_collection
