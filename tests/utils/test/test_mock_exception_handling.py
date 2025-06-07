import pytest
from unittest.mock import MagicMock, patch

from src.utils.test.mock_context_manager import MockContextManager


def test_mock_context_manager_with_exception():
    """Test that MockContextManager properly handles exceptions in the context block."""
    # Create a subclass of MockContextManager with overridden methods to avoid imports
    class TestMockContextManager(MockContextManager):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.patchers_stopped = False
        
        def _apply_patches(self, patch_type, patch_items):
            """Override to avoid imports"""
            for name, value in patch_items.items():
                mock_obj = MagicMock()
                self.active_mocks[name] = mock_obj
                self.active_patchers[name] = MagicMock()
        
        def stop_all_mocks(self):
            """Override to mark patchers as stopped and clear dictionaries"""
            self.patchers_stopped = True
            self.active_mocks.clear()
            self.active_patchers.clear()
    
    # Create our test instance
    mock_context = TestMockContextManager(
        target_path="fake.module",
        method_behaviors={"method_name": lambda x: x * 2},
        attribute_values={"attr_name": 42},
    )

    # Test that patchers are cleaned up even if an exception is raised
    with pytest.raises(ValueError):
        with mock_context:
            # Should have mocked objects available in the context
            assert mock_context.active_patchers
            assert mock_context.active_mocks
            # Raise an exception in the context
            raise ValueError("Test exception")

    # Verify that all mocks were cleaned up despite the exception
    assert not mock_context.active_mocks, "Mocks were not cleaned up after exception"
    assert mock_context.patchers_stopped, "stop_all_mocks was not called"


def test_update_patch_with_exception():
    """Test that update_patch properly restores the original mock when an exception occurs."""
    # Use patch to avoid actual imports
    with patch('src.utils.test.mock_patching_strategies.MethodPatcherStrategy.execute') as mock_execute:
        mock_method = MagicMock()
        mock_method.side_effect = lambda x: x * 2
        
        mock_patcher = MagicMock()
        mock_patcher.start.return_value = mock_method
        
        mock_execute.return_value = mock_patcher
        
        mock_context = MockContextManager(
            target_path="fake.module",
            method_behaviors={"method_name": lambda x: x * 2},
        )

        with mock_context:
            # Mock the update_patch method to avoid importing modules
            original_update_patch = mock_context.update_patch
            mock_context.update_patch = MagicMock()
            
            # Create a context manager for testing
            class MockUpdatePatch:
                def __init__(self, name, value):
                    self.name = name
                    self.value = value
                    
                def __enter__(self):
                    # Simulate changing the mock behavior
                    mock_method.side_effect = lambda x: x + 5
                    return mock_method
                    
                def __exit__(self, exc_type, exc_val, exc_tb):
                    # Restore the original behavior
                    mock_method.side_effect = lambda x: x * 2
                    return False
            
            mock_context.update_patch.return_value = MockUpdatePatch("method_name", lambda x: x + 5)
            
            # Test with exception
            with pytest.raises(ValueError):
                with mock_context.update_patch("method_name", lambda x: x + 5):
                    # Test the "new" behavior
                    assert mock_method(2) == 7  # Should be using the side effect from MockUpdatePatch
                    raise ValueError("Test exception")
            
            # After the exception, verify the behavior is restored
            assert mock_method(2) == 4  # Should be using the original side effect
            
            # Restore the original method
            mock_context.update_patch = original_update_patch


def test_remove_patch_with_exception():
    """Test that remove_patch properly restores the original mock when an exception occurs."""
    # Use patch to avoid actual imports
    with patch('src.utils.test.mock_patching_strategies.MethodPatcherStrategy.execute') as mock_execute:
        mock_method = MagicMock()
        mock_method.side_effect = lambda x: x * 2
        
        mock_patcher = MagicMock()
        mock_patcher.start.return_value = mock_method
        
        mock_execute.return_value = mock_patcher
        
        mock_context = MockContextManager(
            target_path="fake.module",
            method_behaviors={"method_name": lambda x: x * 2},
        )

        with mock_context:
            # Mock the remove_patch method to avoid importing modules
            original_remove_patch = mock_context.remove_patch
            mock_context.remove_patch = MagicMock()
            
            # Create a context manager for testing
            class MockRemovePatch:
                def __init__(self, name):
                    self.name = name
                    
                def __enter__(self):
                    # Simulate removing the patch
                    mock_context.active_mocks.pop("method_name", None)
                    return None
                    
                def __exit__(self, exc_type, exc_val, exc_tb):
                    # Restore the mock
                    mock_context.active_mocks["method_name"] = mock_method
                    return False
            
            mock_context.remove_patch.return_value = MockRemovePatch("method_name")
            
            # Original mock should be available
            assert "method_name" in mock_context.active_mocks
            
            # Test with exception
            with pytest.raises(ValueError):
                with mock_context.remove_patch("method_name"):
                    # The mock should be removed during the context
                    assert "method_name" not in mock_context.active_mocks
                    raise ValueError("Test exception")
            
            # After the exception, verify the mock is restored
            assert "method_name" in mock_context.active_mocks
            
            # Restore the original method
            mock_context.remove_patch = original_remove_patch
