import pytest
from unittest.mock import Mock
from src.utils.abstract.abstract_singleton import SampleConcreteSingleton
from src.utils.test import patch_object


class TestAbstractSingleton:
    """Test class for AbstractSingleton functionality using smart annotations."""

    def test_setup_called_once(self, sample_concrete_singleton):
        """Test that setup can only be called once."""
        # Create a mock with return_value and use patch_object from smart_mock
        mock_setup = Mock(return_value=None)
        with patch_object(sample_concrete_singleton, "_setup", mock_setup):
            sample_concrete_singleton.setup()  # First call should work
            mock_setup.assert_called_once()

            with pytest.raises(RuntimeError, match="has already been called"):
                sample_concrete_singleton.setup()  # Second call should raise an error

    def test_singleton_creation(self, sample_concrete_singleton):
        """Test that only one instance of SampleConcreteSingleton can be created."""
        second_singleton = SampleConcreteSingleton()
        assert second_singleton == sample_concrete_singleton

    def test_delete_and_reinstantiate_singleton(self, sample_concrete_singleton):
        """Test that deleting and re-instantiating the singleton works."""
        # First, create the instance
        sample_concrete_singleton = SampleConcreteSingleton()

        # Ensure the instance is created
        assert sample_concrete_singleton is not None
        assert (
            SampleConcreteSingleton.test_initialization() is True
        )  # Check that the class is initialized

        # Delete the instance
        SampleConcreteSingleton.delete_instance()

        # Ensure the instance was deleted
        assert (
            SampleConcreteSingleton.test_initialization() is False
        )  # Instance should be deleted

        # Recreate the instance after deletion
        singleton_instance_2 = SampleConcreteSingleton()

        # Ensure the new instance is the same type and is created
        assert isinstance(singleton_instance_2, SampleConcreteSingleton)
        assert (
            sample_concrete_singleton is not singleton_instance_2
        )  # Different instances, but valid

        # Setup the new instance
        singleton_instance_2.setup()
        assert (
            SampleConcreteSingleton.test_initialization() is True
        )  # Should be initialized after setup
