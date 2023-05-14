from ..base import Base, NativeDatetimeField
from tortoise import fields

class User(Base):
    username = fields.CharField(index=True, unique=True, max_length=16)
    email = fields.CharField(index=True, unique=True, max_length=255)
    description = fields.CharField(max_length=140, null=True)
    password_hash = fields.CharField(max_length=60)
    activated = fields.BooleanField(default=False)
    banned = fields.BooleanField(default=False)

    last_active = NativeDatetimeField()
    created = NativeDatetimeField()
    login = NativeDatetimeField()

    activation_token = fields.CharField(null=True, max_length=64)
    activation_expire = NativeDatetimeField(null=True)

    password_reset_token = fields.CharField(null=True, max_length=64)
    password_reset_expire = NativeDatetimeField(null=True)

    email_messages: fields.ReverseRelation["EmailMessage"]
    auth_tokens: fields.ReverseRelation["AuthToken"]

    # favourite: fields.ReverseRelation["AnimeFavourite"]
    # watch: fields.ReverseRelation["AnimeWatch"]

    following: fields.ManyToManyRelation["User"] = fields.ManyToManyField(
        "models.User", related_name="followers", through="service_user_followers"
    )

    followers: fields.ManyToManyRelation["User"]

    class Meta:
        table = "service_users"
