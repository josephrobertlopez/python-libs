from io import StringIO
from unittest.mock import patch

import pytest

from src.utils.test.MockMethods import method_called_in_mock


def test_required_argument(sample_concrete_runner):
    # Test when the required argument '--name' is provided.
    with patch("sys.argv", ["program_name", "--name", "Alice", "--age", "25"]):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            sample_concrete_runner.run(*["--name", "Alice", "--age", "25"])
            output = mock_stdout.getvalue()
            assert "Hello Alice, I see you are 25 years old." in output


def test_optional_argument_with_default(sample_concrete_runner):
    # Test when the required argument '--name' is provided, but optional '--age' is not.
    with patch("sys.argv", ["program_name", "--name", "Bob"]):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            sample_concrete_runner.run(*["--name", "Bob"])
            output = mock_stdout.getvalue()
            assert (
                "Hello Bob, I see you are 30 years old." in output
            )  # default age is 30


def test_missing_required_argument(sample_concrete_runner):
    # Test when the required argument '--name' is missing.
    with patch("sys.argv", ["program_name", "--age", "25"]):
        with pytest.raises(SystemExit):  # ArgumentParser should raise an error
            sample_concrete_runner.run(*["--age", "25"])


def test_invalid_argument_type(sample_concrete_runner):
    # Test when an invalid type is passed for '--age'
    with patch(
        "sys.argv", ["program_name", "--name", "Charlie", "--age", "invalid_age"]
    ):
        with pytest.raises(SystemExit):  # ArgumentParser should raise an error
            sample_concrete_runner.run(*["--name", "Charlie", "--age", "invalid_age"])


def test_argument_alias(sample_concrete_runner, mock_sys):
    # Test when '-a' is used instead of '--age'
    with mock_sys.update_patch("argv", ["program_name", "--name", "David", "-a", "40"]):
        sample_concrete_runner.run(*["--name", "David", "-a", "40"])
        assert method_called_in_mock(
            mock_sys.get_mock("stdout"),
            "write",
            "Hello David, I see you are 40 years old.",
        )


def test_no_arguments(sample_concrete_runner, mock_sys):
    with mock_sys:
        with pytest.raises(SystemExit):
            sample_concrete_runner.run()


@pytest.mark.parametrize(
    "args, expected_output",
    [
        (["--name", "Emma", "--age", "20"], "Hello Emma, I see you are 20 years old."),
        (["--name", "Frank"], "Hello Frank, I see you are 30 years old."),
        (["--name", "Grace", "-a", "35"], "Hello Grace, I see you are 35 years old."),
    ],
)
def test_various_argument_combinations(sample_concrete_runner, args, expected_output):
    # Parametrized testing for various combinations of arguments.
    with patch("sys.argv", ["program_name"] + args):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            sample_concrete_runner.run(*args)
            output = mock_stdout.getvalue()
            assert expected_output in output
