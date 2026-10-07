from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from app.database import engine
from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def client(event_loop):
	await engine.dispose()
	async with ASGITransport(app=app) as transport:
		async with AsyncClient(transport=transport, base_url="http://test") as ac:
			yield ac

	await engine.dispose()