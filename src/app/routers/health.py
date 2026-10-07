from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.models import HTTPHealthResponse
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.elastic import es_client

health = APIRouter(prefix="/health")

@health.get(
	"",
    tags=['System'],
    operation_id="checkHealth",
    summary="Healthcheck endpoint",
    description="Checks if postgres and elasticsearch are alive",
    responses={
         200: {
            "model": HTTPHealthResponse,
			"content": {
				"application/json": {
				}
			}
		 }
	}
)
async def check_health(
	db: AsyncSession = Depends(get_db),
):
	try:
		await db.execute(select(1))
		pg_status = 'ok'
	except Exception:
		pg_status = 'fail'

	es_status = 'ok' if await es_client.ping() else 'fail'

	return {
        "status": "ok" if pg_status == "ok" and es_status == "ok" else "unhealthy",
		"services": {
			"postgres": pg_status,
            "elasticsearch": es_status
		}
	}