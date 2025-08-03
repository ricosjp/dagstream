import sys

from dagstream import __version__


def test_version():
    if sys.version_info < (3, 11):
        # For Python versions < 3.11, skip this test
        return

    import tomllib

    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    assert pyproject["project"]["version"] == __version__
