from app.schemas import CustomModel, datetime_pd
from pydantic import Field


# Responses
class ReadResponseBase(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    note: str | None = Field(max_length=2048, examples=["🤯"])
    updated: datetime_pd = Field(examples=[1686088809])
    created: datetime_pd = Field(examples=[1686088809])
    status: str = Field(examples=["reading"])
    chapters: int = Field(examples=[3])
    volumes: int = Field(examples=[3])
    rereads: int = Field(examples=[2])
    score: int = Field(examples=[8])
    start_date: datetime_pd | None
    end_date: datetime_pd | None


class ReadStatsResponse(CustomModel):
    completed: int = Field(examples=[1502335], default=0)
    reading: int = Field(examples=[83106], default=0)
    on_hold: int = Field(examples=[206073], default=0)
    dropped: int = Field(examples=[33676], default=0)
    planned: int = Field(examples=[30222], default=0)
    score_1: int = Field(examples=[3087], default=0)
    score_2: int = Field(examples=[2633], default=0)
    score_3: int = Field(examples=[4583], default=0)
    score_4: int = Field(examples=[11343], default=0)
    score_5: int = Field(examples=[26509], default=0)
    score_6: int = Field(examples=[68501], default=0)
    score_7: int = Field(examples=[211113], default=0)
    score_8: int = Field(examples=[398095], default=0)
    score_9: int = Field(examples=[298198], default=0)
    score_10: int = Field(examples=[184038], default=0)
