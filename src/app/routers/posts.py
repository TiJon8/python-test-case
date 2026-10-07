from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import delete, select

from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.elastic import delete_post_from_es, find_posts
from app.models import HTTPPostsResponse, HTTPErrorResponse
from app.database import Document

posts = APIRouter(prefix="/posts")

@posts.get(
		"/search",
        response_model=HTTPPostsResponse,
        operation_id="getPostBySearch",
        summary="finds posts related to text search",
        tags=["Posts"],
        responses={
             404: {
            	"model": HTTPErrorResponse,
            	"description": "Not Found",
            	"content": {
                	"application/json": {
                    	"example": {"detail": "No matchings found"}
                	}
            	}
        	}
		}
)
async def search(
    q: Annotated[str, Query(min_length=1, description="Строка поиска", examples=["Новй скин"])],
    db: AsyncSession = Depends(get_db)
):
	post_ids = await find_posts(q, limit=100)
	if not post_ids:
		raise HTTPException(status_code=404, detail="No matchings found")
    
	stmt = (
        select(Document)
        .where(Document.id.in_(post_ids))
        .order_by(Document.created_date.desc())
        .limit(20)
    )
	result = await db.execute(stmt)
	posts = result.scalars().all()

	return HTTPPostsResponse(
        count=len(posts),
        posts=posts
	)



@posts.delete(
        "/{post_id}",
        status_code=204,
        operation_id="deletePost",
        description="""
		This will delete the record from the database and the index.
		""",
		summary="deletes post by ID",
		tags=["Posts"],
        responses={
			404: {
				"model": HTTPErrorResponse,
				"description": "Not Found",
				"content": {
					"application/json": {
						"example": {"detail": "ID not found"}
					}
				}
			}
		}
)
async def delete_document(
     post_id: Annotated[int, Path(title="Post ID", gt=0, examples=[2])],
     db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.id == post_id)
    res = await db.execute(stmt)
    post = res.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.execute(delete(Document).where(Document.id == post_id))
    await db.commit()
    
    await delete_post_from_es(post_id)
    
    return None

