from app.auth.service import build_redirect_url


def test_redirect_url_legacy():
    reference = "request-reference"

    result = build_redirect_url(
        "hikka://auth/?state=legacy", reference
    )

    assert result == f"hikka://auth/?reference={reference}"


def test_redirect_url_reference_query_parameter():
    reference = "request-reference"

    result = build_redirect_url(
        "https://example.com/auth?reference={reference}&state=keep",
        reference,
    )

    assert result == (
        "https://example.com/auth?reference=request-reference&state=keep"
    )


def test_redirect_url_reference_path():
    reference = "request-reference"

    result = build_redirect_url(
        "https://example.com/auth/{reference}/confirm", reference
    )

    assert result == "https://example.com/auth/request-reference/confirm"


def test_redirect_url_replaces_all_references_and_encodes_value():
    reference = "value /?&+#% є"

    result = build_redirect_url(
        "https://example.com/{reference}?reference={reference}", reference
    )

    encoded_reference = "value%20%2F%3F%26%2B%23%25%20%D1%94"
    assert result == (
        f"https://example.com/{encoded_reference}?reference={encoded_reference}"
    )


def test_redirect_url_template_does_not_normalize_endpoint():
    reference = "request-reference"
    endpoint = (
        "https://example.com/a%2Fb?state=keep%2Bvalue&reference={reference}"
        "#fragment"
    )

    result = build_redirect_url(endpoint, reference)

    assert result == (
        "https://example.com/a%2Fb?state=keep%2Bvalue&"
        "reference=request-reference#fragment"
    )
