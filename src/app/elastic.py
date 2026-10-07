import asyncio
import os
import logging
from elasticsearch import AsyncElasticsearch, ConnectionTimeout, NotFoundError
from elasticsearch.helpers import async_bulk
from elasticsearch.exceptions import ApiError

logger = logging.getLogger(__name__)

ELASTICSEARCH_URL = os.getenv("ES_URL")
INDEX_NAME = os.getenv("ES_INDEX")

es_client = AsyncElasticsearch(
    ELASTICSEARCH_URL,
    request_timeout=30.0,
    max_retries=3,
    retry_on_timeout=True
)

async def wait_for_elasticsearch(max_retries: int = 10, delay: int = 3):
    for attempt in range(1, max_retries + 1):
        try:
            if await es_client.ping():
                logger.info("Elasticsearch готов к работе!")
                return
        except (ConnectionError, ConnectionTimeout):
            pass
        
        logger.info(f"Waiting for Elasticsearch (try {attempt}/{max_retries})...")
        await asyncio.sleep(delay)
    
    raise RuntimeError("Failed cennect to ElasticSearch")


async def init_elasticsearch(seeded_posts: list[dict] | None = None) -> None:
    index_exists = False
    try:
        index_exists = await es_client.indices.exists(index=INDEX_NAME)
    except ApiError as err:
        if err.status_code in (400, 404):
            logger.warning(f"Index {INDEX_NAME} not found. Status: {err.status_code}")
            index_exists = False
        else:
            raise err

    if not index_exists:
        logger.info(f"Creating an index '{INDEX_NAME}'...")
        try:
            await es_client.indices.create(
                index=INDEX_NAME,
                settings={
        			"number_of_shards": 1,
        			"number_of_replicas": 0
    			},
                mappings={
                    "properties": {
                        "id": {"type": "integer"},
                        "text": {"type": "text", "analyzer": "standard"}
                    }
                }
            )
            await es_client.cluster.health(
				index=INDEX_NAME, 
				wait_for_status="yellow", 
				request_timeout=30.0
        	)
            logger.info(f"Index '{INDEX_NAME}' succesfully created.")
        except ApiError as err:
            if "resource_already_exists_exception" in str(err):
                logger.warning("Index already created")
            else:
                raise err
    
    count_resp = await es_client.count(index=INDEX_NAME)
    if count_resp["count"] == 0 and seeded_posts:
        logger.info(f"Заливка {len(seeded_posts)} документов в индекс")
        actions = [
            {
                "_index": INDEX_NAME,
                "_source": {
                    "id": post["id"],
                    "text": post["text"]
                }
            }
            for post in seeded_posts
        ]
        success, failed = await async_bulk(es_client, actions)
        logger.info(f"Index seeded. Success: {success}, Failed: {len(failed)}")


async def find_posts(query: str, limit: int = 100) -> list[int]:
    try:
        response = await es_client.search(
            index=INDEX_NAME,
            query={
                "match": {
                    "text": {
						"query": query,
                    	"operator": "and"
					}
                }
            },
            size=limit
        )
        
        ids = [hit["_source"]["id"] for hit in response["hits"]["hits"]]
        return ids
    except NotFoundError:
        logger.warning(f"Index '{INDEX_NAME}' not found")
        return []


async def delete_post_from_es(post_id: int) -> None:
    await es_client.delete_by_query(
        index=INDEX_NAME,
        query={"match": {"id": post_id}}
    )