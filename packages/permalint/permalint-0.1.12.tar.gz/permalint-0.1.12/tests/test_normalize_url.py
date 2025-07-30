import pytest

from permalint import normalize_url


@pytest.mark.parametrize(
    ("input_url", "expected"),
    [
        (
            "https://github.com/user/repo?utm_source=foo#readme",
            "github.com/user/repo",
        ),
        ("http://github.com/user/repo/", "github.com/user/repo"),
        ("https://www.github.com/user/repo", "github.com/user/repo"),
        ("https://github.com/user/repo/issues/123", "github.com/user/repo"),
        ("https://github.com/user/repo/", "github.com/user/repo"),
        ("https://github.com/user", "github.com/user"),
        ("https://www.example.com/foo/bar?baz=1#frag", "example.com/foo/bar"),
        ("http://example.com/", "example.com"),
        ("https://www.example.com/", "example.com"),
        ("example.com/foo", "example.com/foo"),
        ("https://example.com", "example.com"),
        ("https://example.com/", "example.com"),
        ("https://rye.astral.sh/", "rye.astral.sh"),
        ("https://rye-up.com/", "rye-up.com"),
        ("http://molefrog.github.com/rye", "molefrog.github.com/rye"),
        ("https://bpython-interpreter.org", "bpython-interpreter.org"),
        (
            "https://files.pythonhosted.org/packages/ba/dd/cc02bf66f342a4673867fdf6c1f9fce90ec1e91e651b21bc4af4890101da/bpython-0.25.tar.gz",
            "files.pythonhosted.org/packages/ba/dd/cc02bf66f342a4673867fdf6c1f9fce90ec1e91e651b21bc4af4890101da/bpython-0.25.tar.gz",
        ),
        (
            "https://files.pythonhosted.org/packages/cf/76/54e0964e2974becb673baca69417b6c6293e930d4ebcf2a2a68c1fe9704a/bpython-0.24.tar.gz",
            "files.pythonhosted.org/packages/cf/76/54e0964e2974becb673baca69417b6c6293e930d4ebcf2a2a68c1fe9704a/bpython-0.24.tar.gz",
        ),
        (
            "github.com/MatteoBax/ascii-progressbar.git",
            "github.com/MatteoBax/ascii-progressbar",
        ),
        (
            "https://github.com/seymoe/mieo.git",
            "github.com/seymoe/mieo",
        ),
        ("git+https://github.com/seymoe/mieo.git", "github.com/seymoe/mieo"),
        (
            "git@github.com:chf007/egg-qywx-login.git",
            "github.com/chf007/egg-qywx-login",
        ),
        (
            "git+ssh://git@github.com/bartdominiak/vue-snap.git",
            "github.com/bartdominiak/vue-snap",
        ),
        (
            "git://github.com/biggora/express-useragent.git",
            "github.com/biggora/express-useragent",
        ),
        (
            "http://",
            "",
        ),
        (
            "https://[laoyang666].github.io/github-actions-demo",
            "",
        ),
        ('http://  "files": [', ""),
    ],
)
def test_normalize_url(input_url: str, expected: str) -> None:
    assert normalize_url(input_url) == expected
