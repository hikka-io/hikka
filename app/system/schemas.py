from app.schemas import CustomModel


# Args
class EventArgs(CustomModel):
    r: str | None
    d: str
    n: str
    u: str
