from io import StringIO
import pytest
from unittest.mock import Mock
from src.utils.abstract.abstract_runner import AbstractRunner
from tests.shared_annotations import (
    runner_test,
    output_test,
    create_runner_test_cases,
    mock_test_sys,
)


@runner_test(argv=["program_name", "--name", "Alice", "--age", "25"])
@output_test()
def test_required_argument(sample_concrete_runner, **kwargs):
    """Test when the required argument '--name' is provided."""
    sample_concrete_runner.run(*["--name", "Alice", "--age", "25"])
    captured_output = kwargs["captured_stdout"].getvalue()
    assert "Hello Alice, I see you are 25 years old." in captured_output


@runner_test(argv=["program_name", "--name", "Bob"])
@output_test()
def test_optional_argument_with_default(sample_concrete_runner, **kwargs):
    """Test when required argument '--name' is provided, but optional '--age' is not."""
    sample_concrete_runner.run(*["--name", "Bob"])
    captured_output = kwargs["captured_stdout"].getvalue()
    assert "Hello Bob, I see you are 30 years old." in captured_output


@mock_test_sys(argv=["program_name", "--age", "25"])
def test_missing_required_argument(sample_concrete_runner):
    """Test when the required argument '--name' is missing."""
    with pytest.raises(SystemExit):  # ArgumentParser should raise an error
        sample_concrete_runner.run(*["--age", "25"])


@mock_test_sys(argv=["program_name", "--name", "Charlie", "--age", "invalid_age"])
def test_invalid_argument_type(sample_concrete_runner):
    """Test when an invalid type is passed for '--age'."""
    with pytest.raises(SystemExit):  # ArgumentParser should raise an error
        sample_concrete_runner.run(*["--name", "Charlie", "--age", "invalid_age"])


@runner_test(argv=["program_name", "--name", "David", "-a", "40"])
@output_test()
def test_argument_alias(sample_concrete_runner, **kwargs):
    """Test when '-a' is used instead of '--age'."""
    sample_concrete_runner.run(*["--name", "David", "-a", "40"])
    captured_output = kwargs["captured_stdout"].getvalue()
    assert "Hello David, I see you are 40 years old." in captured_output


@mock_test_sys(argv=["program_name"])
def test_no_arguments(sample_concrete_runner):
    """Test when no arguments are provided."""
    with pytest.raises(SystemExit):
        sample_concrete_runner.run()


test_cases = {
    "basic": ["--name", "Alice", "--age", "25"],
    "minimal": ["--name", "Bob"],
    "complex": ["--name", "Charlie", "--age", "30", "--city", "Seattle"],
}


@pytest.mark.parametrize(
    "args, expected_output",
    [
        (["--name", "Alice", "--age", "25"], "Alice"),
        (["--name", "Bob"], "Bob"),
        (["--name", "Charlie", "--age", "30"], "Charlie"),
    ],
)
def test_various_argument_combinations(sample_concrete_runner, args, expected_output):
    """Parametrized testing for various combinations of arguments."""

    @runner_test(argv=["program_name"] + args)
    @output_test()
    def run_test(**kwargs):
        sample_concrete_runner.run(*args)
        captured_output = kwargs["captured_stdout"].getvalue()
        assert expected_output in captured_output

    run_test()
