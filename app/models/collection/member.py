from sqlalchemy import ForeignKey, String, UniqueConstraint, Index, text
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from datetime import datetime
from app import constants
from ..base import Base

from ..mixins import (
    CreatedMixin,
    UpdatedMixin,
)


class CollectionMember(CreatedMixin, UpdatedMixin, Base):
    __tablename__ = "service_collection_members"
    __table_args__ = (
        UniqueConstraint("collection_id", "user_id"),
        Index(
            "ix_collection_member_owner",
            "collection_id",
            unique=True,
            postgresql_where=text(
                f"role = '{constants.COLLECTION_MEMBER_OWNER}'"
            ),
        ),
        Index(
            "ix_collection_member_user",
            "user_id",
            "status",
        ),
        Index(
            "ix_collection_member_owner_offer",
            "collection_id",
            unique=True,
            postgresql_where=text("owner_offered_at IS NOT NULL"),
        ),
    )

    status: Mapped[str] = mapped_column(String(16))
    role: Mapped[str] = mapped_column(String(16))

    # Standing offer to hand this member the collection. Kept apart from
    # role and status on purpose: an offer must not touch the rights the
    # member already has, and get_collection_member returns only accepted
    # rows by default, so overloading status would strip their editor
    # access while the offer is outstanding
    owner_offered_at: Mapped[datetime] = mapped_column(nullable=True)

    collection_id = mapped_column(
        ForeignKey("service_collections.id", ondelete="CASCADE"),
        nullable=False,
    )
    collection: Mapped["Collection"] = relationship(
        foreign_keys=[collection_id],
    )

    user_id = mapped_column(
        ForeignKey("service_users.id"),
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        foreign_keys=[user_id],
    )

    invited_by_id = mapped_column(
        ForeignKey("service_users.id"), nullable=True
    )
    invited_by: Mapped["User"] = relationship(
        foreign_keys=[invited_by_id],
    )
