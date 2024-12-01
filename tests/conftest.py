from unittest.mock import Mock

import pytest
from src.utils.test.MockManager import MockManager


@pytest.fixture
def mock_sleep(mocker):
    """Fixture to mock time.sleep to avoid actual delays."""
    return mocker.patch("time.sleep", autospec=True)


@pytest.fixture
def mock_sys():
    """
    Preconfigured MockFixture for sys module.
    """
    default_attr = {
        "frozen": True,
        "executable": "fake_executable_path",
        "_MEIPASS": "pyinstaller/path",
    }
    return MockManager(target_path="sys", attribute_values=default_attr)


@pytest.fixture
def mock_os():
    default_behaviors = {"path.exists": True,
                         "environ": {"TEST_VAR": "test_value"},
                         "path.join": lambda *args: "/".join(args),
                         "makedirs": True,
                         }
    return MockManager(target_path="os", method_behaviors=default_behaviors)

@pytest.fixture
def mock_builtins():
    default_behaviors = {
        "open":Mock()
    }
    return MockManager(target_path="builtins",method_behaviors=default_behaviors)