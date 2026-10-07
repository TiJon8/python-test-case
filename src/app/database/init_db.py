import ast
import csv
from datetime import datetime
import logging
from sqlalchemy import select
from app.database import AsyncSessionLocal, engine
from app.database.schemas import Document, Base

CSV_PATH = "posts.csv"

logger = logging.getLogger(__name__)

def parse_rubrics(rubrics_str: str) -> list[str]:
    try:
        parsed = ast.literal_eval(rubrics_str)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
        return [str(parsed)]
    except (ValueError, SyntaxError):
        return [r.strip() for r in rubrics_str.strip("[]'\"").split(",") if r.strip()]


async def init_db_and_seed() -> list[dict]:
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
	
	async with AsyncSessionLocal() as session:
		stmt = select(Document.id).limit(1)
		result = await session.execute(stmt)
		has_data = result.scalar_one_or_none() is not None

		if has_data:
			return []
        
		logger.info("Database is empty")
		posts_to_insert = []
		with open(CSV_PATH, mode="r", encoding="utf-8") as file:
			reader = csv.DictReader(file)
			for row in reader:
				p = Document(
					text=row["text"],
					created_date=datetime.strptime(row["created_date"], "%Y-%m-%d %H:%M:%S"),
					rubrics=parse_rubrics(row["rubrics"])
				)
				posts_to_insert.append(p)

		session.add_all(posts_to_insert)
		await session.commit()
        
		logger.info(f"Loaded {len(posts_to_insert)} records to tadabase.")
		seeded_posts = [
			{"id": post.id, "text": post.text}
			for post in posts_to_insert
		]
        
		return seeded_posts