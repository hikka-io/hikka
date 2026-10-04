from app.schemas import CustomModel


class MagazineResponse(CustomModel):
    name_en: str
    slug: str
