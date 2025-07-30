from extratools_html import get_cache_key


def test_get_cache_key() -> None:
    assert (
        get_cache_key("https://localhost")
        == get_cache_key("https://localhost/")
        == get_cache_key("https://localhost/?")
        == get_cache_key("https://localhost/#somewhere")
        == "localhost/?"
    )

    assert (
        get_cache_key("https://localhost/?q=query")
        == get_cache_key("https://localhost/?q=query#somewhere")
        == "localhost/?q=query"
    )

    assert (
        get_cache_key("https://localhost/foo")
        == get_cache_key("https://localhost/foo?")
        == get_cache_key("https://localhost/foo#somewhere")
        == "localhost/foo"
    )

    assert (
        get_cache_key("https://localhost/foo?q=query")
        == get_cache_key("https://localhost/foo?q=query#somewhere")
        == "localhost/foo?q=query"
    )

    assert (
        get_cache_key("https://localhost/foo/")
        == get_cache_key("https://localhost/foo/?")
        == get_cache_key("https://localhost/foo/#somewhere")
        == "localhost/foo/?"
    )

    assert (
        get_cache_key("https://localhost/foo/bar")
        == get_cache_key("https://localhost/foo/bar?")
        == get_cache_key("https://localhost/foo/bar#somewhere")
        == "localhost/foo/bar"
    )

    assert (
        get_cache_key("https://localhost/foo/bar?q=query")
        == "localhost/foo/bar?q=query"
    )
