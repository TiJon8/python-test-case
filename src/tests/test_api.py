import pytest

@pytest.mark.asyncio
async def test_health_check(client):
	res = await client.get("/health")
	data = res.json()
	assert res.status_code == 200 and data["status"] == "ok"
	assert "postgres" in data["services"]


@pytest.mark.asyncio
async def test_find_posts_without_query(client):
	res = await client.get("/posts/search")
	assert res.status_code == 422

