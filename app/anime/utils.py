from sqlalchemy import desc, asc


def build_order_by(sort: list[str]):
    return [
        desc(field) if order == "desc" else asc(field)
        for field, order in (entry.split(":") for entry in sort)
    ] + [desc("content_id")]
