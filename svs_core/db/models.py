# TODO: maybe remove type: ignore[misc] punishment for using DeclarativeBase
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):  # type: ignore[misc]
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class UserModel(IDMixin, TimestampMixin, Base):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    @classmethod
    def create(
        cls, name: str, *, ssh_keys: Optional[list["UserModel"]] = None
    ) -> "UserModel":
        user = cls()
        user.name = name
        return user
