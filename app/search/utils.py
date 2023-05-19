from sqlalchemy import desc, asc
from enum import Enum


def enum_list_values(enum_list: list[Enum]):
    return [color.value for color in enum_list]


def build_order_by(sort: list[str]):
    return [
        desc(field) if order == "desc" else asc(field)
        for field, order in (entry.split(":") for entry in sort)
    ]
