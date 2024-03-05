from pydantic import Field, field_validator
from app.schemas import CustomModel


# Args
class MALAnimeArgs(CustomModel):
    mal_ids: list[int] = Field(min_length=1, max_length=500)

    @field_validator("mal_ids")
    def validate_mal_id(cls, mal_ids):
        if len(list(set(mal_ids))) != len(mal_ids):
            raise ValueError("Duplicated mal_id")

        return mal_ids
