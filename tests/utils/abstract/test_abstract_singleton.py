import pytest
from unittest.mock import patch
from src.utils.abstract.abstract_singleton import SampleConcreteSingleton


@pytest.fixture
def sample_concrete_singleton():
    """Fixture to instantiate the SampleConcreteSingleton."""
    return SampleConcreteSingleton()


def test_singleton_creation(sample_concrete_singleton):
    """Test that only one instance of SampleConcreteSingleton can be created."""
    second_singleton = SampleConcreteSingleton()
    assert second_singleton == sample_concrete_singleton


def test_setup_called_once(sample_concrete_singleton):
    """Test that setup can only be called once."""
    # We will patch the setup process (not pygame this time)
    with patch.object(sample_concrete_singleton, '_setup', return_value=None) as mock_setup:
        sample_concrete_singleton.setup()  # First call should work
        mock_setup.assert_called_once()

        with pytest.raises(RuntimeError, match="has already been called"):
            sample_concrete_singleton.setup()  # Second call should raise an error


def test_delete_and_reinstantiate_singleton():
    """Test that deleting and re-instantiating the singleton works."""
    # First, create the instance
    singleton_instance_1 = SampleConcreteSingleton()

    # Ensure the instance is created
    assert singleton_instance_1 is not None
    assert SampleConcreteSingleton.test_initialization() is True  # Check that the class is initialized

    # Delete the instance
    SampleConcreteSingleton.delete_instance()

    # Ensure the instance was deleted
    assert SampleConcreteSingleton.test_initialization() is False  # Instance should be deleted

    # Recreate the instance after deletion
    singleton_instance_2 = SampleConcreteSingleton()

    # Ensure the new instance is the same type and is created
    assert isinstance(singleton_instance_2, SampleConcreteSingleton)
    assert singleton_instance_1 is not singleton_instance_2  # Different instances, but valid

    # Setup the new instance
    singleton_instance_2.setup()
    assert SampleConcreteSingleton.test_initialization() is True  # Should be initialized after setup
