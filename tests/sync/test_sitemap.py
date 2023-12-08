from app.sync.sitemap import generate_sitemap


async def test_sitemap(test_session, aggregator_anime):
    result = await generate_sitemap(test_session)

    assert len(result) == 17
    assert result[0]["slug"] == "fullmetal-alchemist-brotherhood-fc524a"
    assert (
        result[16]["slug"]
        == "pia-carrot-e-youkoso-sayaka-no-koi-monogatari-227414"
    )
