"""Zone Activity Model"""

from sqlalchemy import Integer, String, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from artemis_model.base import AuditMixin, TimeStampMixin, CustomSyncBase, CustomBase


class PlayerActivityMixin(TimeStampMixin, AuditMixin):
    """User activity log, sorted by created_at DESC for retrieval"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, nullable=False)
    activity_type: Mapped[str] = mapped_column(String, nullable=False)
    activity_data: Mapped[dict] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_player_activity_player_created", "player_id", "created_at".desc()),
        Index("idx_player_activity_created", "created_at".desc()),
    )


class PlayerActivitySync(CustomSyncBase, PlayerActivityMixin):
    """Sync model for Player Activity"""
    pass


class PlayerActivity(CustomBase, PlayerActivityMixin):
    """Base model for Player Activity"""
    pass
