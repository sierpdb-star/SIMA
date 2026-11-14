
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime, timezone

from app.database import Base


class CampaignContent(Base):
    __tablename__ = "campaign_contents"

    id = Column(Integer, primary_key=True, index=True)

    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.id"),
        nullable=False,
        unique=True
    )

    content_type = Column(
        String,
        nullable=False,
        default="text"
    )

    text_content = Column(Text, nullable=True)
    media_url = Column(String, nullable=True)
    media_type = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
