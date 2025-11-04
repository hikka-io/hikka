import json
from app.common.schemas import Document

with open("dotest.json", "r") as file:
    test = json.load(file)

    Document(nodes=test)
