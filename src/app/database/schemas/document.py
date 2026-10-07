from datetime import datetime
from sqlalchemy import ARRAY, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .. import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rubrics: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)