import pytest

from permalint import possible_names


@pytest.mark.parametrize(
    ("input_name", "probable_names"),
    [
        (
            "https://taku910.github.io/mecab/",
            ["taku910.github.io/mecab", "mecab"],
        ),
        (
            "https://taku910.github.io/mecab-ipadic/",
            ["taku910.github.io/mecab-ipadic", "mecab-ipadic"],
        ),
        # in this case, the last path segment is the name
        ("mozilla.org/cbindgen", ["mozilla.org/cbindgen", "cbindgen"]),
        # there's no path here, so we can check out the subdomain and domain
        (
            "poppler.freedesktop.org",
            ["poppler.freedesktop.org", "poppler", "freedesktop"],
        ),
        # there's a path here, so we're really only interested in the last
        # segment
        (
            "poppler.freedesktop.org/poppler-data",
            ["poppler.freedesktop.org/poppler-data", "poppler-data"],
        ),
        ("elfutils.org", ["elfutils.org", "elfutils"]),
        ("hdfgroup.org/HDF5", ["hdfgroup.org/HDF5", "HDF5", "hdf5"]),
    ],
)
def test_possible_names(input_name: str, probable_names: list[str]) -> None:
    assert possible_names(input_name) == probable_names
