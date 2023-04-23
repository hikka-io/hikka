from ..base import Base, NativeDatetimeField
from tortoise import fields

class AuthToken(Base):
    secret = fields.CharField(index=True, unique=True, max_length=64)
    expiration = NativeDatetimeField()
    created = NativeDatetimeField()

    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="auth_tokens"
    )

    class Meta:
        table = "service_auth_tokens"
