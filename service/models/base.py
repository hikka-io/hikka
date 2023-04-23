from tortoise.models import Model
from datetime import datetime
from tortoise import fields

class Base(Model):
    id = fields.UUIDField(pk=True)

    @property
    def reference(self):
        return str(self.id)

class NativeDatetimeField(fields.Field[datetime], datetime):
    SQL_TYPE = "TIMESTAMP"
