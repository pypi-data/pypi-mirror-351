import pytest

from permalint import is_canonical_url


@pytest.mark.parametrize(
    ("input_url", "expected"),
    [
        ("https://github.com/user/repo?utm_source=foo#readme", False),
        ("http://github.com/user/repo/", False),
        ("github.com/user/repo", True),
        ("https://bpython-interpreter.org", False),
        ("github.com/MatteoBax/ascii-progressbar.git", False),
        ("git+ssh://git@github.com/bartdominiak/vue-snap.git", False),
        ("git://github.com/biggora/express-useragent.git", False),
    ],
)
def test_is_canonical_url(input_url: str, expected: bool) -> None:
    assert is_canonical_url(input_url) == expected
