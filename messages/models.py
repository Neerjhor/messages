from sqlmodel import SQLModel, Field, Index
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

class User(SQLModel, table=True):
    name: str
    username: str = Field(nullable=False, unique=True, primary_key=True)
    last_seen: datetime | None = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))

class Message(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    sender_username: str
    recipient_username: str = Field(index=True)
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))

    # A composite index created with recipient_username and timestamp.
    __table_args__ = (
        Index('idx_messages_recipient_timestamp', 'recipient_username', 'timestamp'),
    )