import aiofiles
import aiohttp
import asyncio
import json


ANIME_LIST = {
    "fc524a18-378f-4ccb-82a0-b4063206c600": "fma.json",
    "f297970c-93e7-47f0-a01d-ee4cd1f067d9": "steins_gate.json",
    "a3ac0776-67f6-474b-83ba-7df7a3c2e3f6": "kaguya_1.json",
    "73a73ca9-fcea-4521-ad88-fa5206ad8e78": "kaguya_2.json",
    "fcd76158-66b6-4c72-8c1c-5aa801a5efff": "kaguya_3.json",
}


async def load_json(path):
    async with aiofiles.open(path, mode="r") as file:
        contents = await file.read()
        return json.loads(contents)


async def get_test_people():
    people = []

    for slug in ANIME_LIST:
        data = await load_json(
            f"tests/aggregator/data/anime_info/{ANIME_LIST[slug]}"
        )

        for entry in data["staff"] + data["voices"]:
            if entry["person"]["content_id"] not in people:
                people.append(entry["person"]["content_id"])

    result = []

    for content_id in people:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost:7777/database/person/{content_id}"
            ) as r:
                data = await r.json()
                result.append(data)

    print(json.dumps(result))


async def get_test_characters():
    characters = []

    for slug in ANIME_LIST:
        data = await load_json(
            f"tests/aggregator/data/anime_info/{ANIME_LIST[slug]}"
        )

        for entry in data["characters"]:
            if entry["character"]["content_id"] not in characters:
                characters.append(entry["character"]["content_id"])

    result = []

    for content_id in characters:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost:7777/database/character/{content_id}"
            ) as r:
                data = await r.json()
                result.append(data)

    print(json.dumps(result))


if __name__ == "__main__":
    asyncio.run(get_test_characters())
    # asyncio.run(get_test_people())
