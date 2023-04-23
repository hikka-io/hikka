from ..base import Base, NativeDatetimeField
from tortoise import fields

class EmailMessage(Base):
    sent_time = NativeDatetimeField(default=None, null=True)
    sent = fields.BooleanField(default=False)
    type = fields.CharField(max_length=32)
    created = NativeDatetimeField()
    content = fields.TextField()

    receiver: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="email_messages"
    )

    class Meta:
        table = "service_email_messages"
