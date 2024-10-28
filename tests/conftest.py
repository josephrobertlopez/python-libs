import pytest
import sys


@pytest.fixture
def mock_sleep(mocker):
    """Fixture to mock time.sleep to avoid actual delays."""
    return mocker.patch("time.sleep", autospec=True)


@pytest.fixture
def mock_sys_argv(mocker):
    """Fixture to mock sys.argv for testing main function."""
    def _mock_sys_argv(test_args):
        mocker.patch.object(sys, 'argv', test_args)
    return _mock_sys_argv
