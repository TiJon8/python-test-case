from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

class DocumentModel(BaseModel):
	id: int
	text: str
	rubrics: list[str]
	created_date: datetime

	model_config = ConfigDict(from_attributes=True)

class HTTPPostsResponse(BaseModel):
	count: int = Field()
	posts: list[DocumentModel]

	model_config = ConfigDict(from_attributes=True)

class HTTPErrorResponse(BaseModel):
    detail: str = Field()


class HealthAppStatusEnum(str, Enum):
	OK="ok"
	UNHEALTHY="unhealthy"

class HealthStatusEnum(str, Enum):
	OK="ok"
	FAIL="fail"

class HtalthServices(BaseModel):
	postgres: HealthStatusEnum = Field()
	elasticsearch: HealthStatusEnum = Field()

class HTTPHealthResponse(BaseModel):
	status: HealthAppStatusEnum = Field()
	services: HtalthServices