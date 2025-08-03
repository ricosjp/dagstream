import tomllib

from dagstream import __version__


def test_version():
    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    assert pyproject["project"]["version"] == __version__
