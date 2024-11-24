import pytest
from src.utils.test.MockFixture import MockFixture


@pytest.fixture
def mock_sleep(mocker):
    """Fixture to mock time.sleep to avoid actual delays."""
    return mocker.patch("time.sleep", autospec=True)


@pytest.fixture
def mock_sys():
    """
    Preconfigured MockFixture for sys module
    """
    default_behaviors = {
        "frozen": False,
        "executable": "fake_executable_path",
        "_MEIPASS": "pyinstaller/path"
    }
    return MockFixture(mock_path="sys",
                       default_behaviors=default_behaviors)
