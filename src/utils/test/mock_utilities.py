"""
Core Mock Utilities and Context Management

This module provides the low-level mock utilities, context managers, and patching
strategies that power the runtime annotations framework. It consolidates all the
core mocking functionality into a single, efficient module.

Features:
- Smart context management with automatic cleanup
- Multiple patching strategies for different scenarios
- Mock factories and builders
- Exception-safe context handling
- Advanced mock introspection
"""

import functools
import importlib
import threading
import time
from typing import Any, Dict, List, Optional, Type, Union, Callable
from unittest.mock import patch, Mock, MagicMock, PropertyMock
from contextlib import contextmanager
from collections import defaultdict


# =============================================================================
# CORE CONTEXT MANAGER
# =============================================================================

class SmartMockContext:
    """Advanced context manager with automatic mock detection and cleanup."""
    
    def __init__(self, target_path: str, auto_mock: Optional[Dict[str, Any]] = None, **kwargs):
        """Initialize context with target path and mock configurations."""
        self.target_path = target_path
        self.mock_config = auto_mock or kwargs
        self.active_patches = []
        self.mock_registry = {}
        self.cleanup_callbacks = []
        
    def __enter__(self):
        """Enter context and apply all mocks."""
        self._apply_mocks()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and clean up all patches."""
        self._cleanup_patches()
        self._run_cleanup_callbacks()
        
    def _apply_mocks(self):
        """Apply all configured mocks using appropriate strategies."""
        for attr_name, mock_value in self.mock_config.items():
            try:
                patcher = self._create_patcher(attr_name, mock_value)
                if patcher:
                    mock_obj = patcher.start()
                    self.active_patches.append(patcher)
                    self.mock_registry[attr_name] = mock_obj
            except Exception as e:
                print(f"Warning: Could not patch {self.target_path}.{attr_name}: {e}")
                
    def _create_patcher(self, attr_name: str, mock_value: Any):
        """Create appropriate patcher based on mock value type."""
        full_path = f"{self.target_path}.{attr_name}"
        
        # Strategy 1: Callable with side_effect
        if callable(mock_value) and not isinstance(mock_value, (type, Mock)):
            return patch(full_path, side_effect=mock_value)
            
        # Strategy 2: Mock objects
        elif isinstance(mock_value, (Mock, MagicMock)):
            return patch(full_path, mock_value)
            
        # Strategy 3: Direct value replacement
        else:
            return patch(full_path, mock_value)
            
    def _cleanup_patches(self):
        """Clean up all active patches."""
        for patcher in reversed(self.active_patches):
            try:
                patcher.stop()
            except Exception:
                pass  # Ignore cleanup errors
        self.active_patches.clear()
        self.mock_registry.clear()
        
    def _run_cleanup_callbacks(self):
        """Run all registered cleanup callbacks."""
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception:
                pass  # Ignore callback errors
        self.cleanup_callbacks.clear()
        
    def add_mock(self, attr_name: str, mock_value: Any):
        """Add a new mock during runtime."""
        full_path = f"{self.target_path}.{attr_name}"
        try:
            patcher = self._create_patcher(attr_name, mock_value)
            if patcher:
                mock_obj = patcher.start()
                self.active_patches.append(patcher)
                self.mock_registry[attr_name] = mock_obj
                return mock_obj
        except Exception as e:
            print(f"Warning: Could not add mock {full_path}: {e}")
            return None
            
    def update_mock(self, attr_name: str, new_value: Any):
        """Update an existing mock with new value."""
        # Remove existing mock
        self.remove_mock(attr_name)
        # Add new mock
        return self.add_mock(attr_name, new_value)
        
    def remove_mock(self, attr_name: str):
        """Remove a specific mock."""
        # Find and stop the patcher for this attribute
        for i, patcher in enumerate(self.active_patches):
            if hasattr(patcher, 'attribute') and patcher.attribute == attr_name:
                try:
                    patcher.stop()
                    self.active_patches.pop(i)
                    self.mock_registry.pop(attr_name, None)
                    break
                except Exception:
                    pass
                    
    def get_mock(self, attr_name: str) -> Any:
        """Get a mock object by attribute name."""
        # Return the mock from registry if it exists
        if attr_name in self.mock_registry:
            return self.mock_registry[attr_name]
        
        # If not in registry, try to get the actual patched attribute
        try:
            module_parts = self.target_path.split('.')
            module = importlib.import_module(module_parts[0])
            for part in module_parts[1:]:
                module = getattr(module, part)
            return getattr(module, attr_name, None)
        except (ImportError, AttributeError):
            return None
        
    def register_cleanup(self, callback: Callable):
        """Register a cleanup callback."""
        self.cleanup_callbacks.append(callback)


# =============================================================================
# SMART PATCHING STRATEGIES
# =============================================================================

class PatchingStrategy:
    """Base class for patching strategies."""
    
    def can_handle(self, mock_value: Any) -> bool:
        """Check if this strategy can handle the mock value."""
        raise NotImplementedError
        
    def create_patcher(self, target_path: str, mock_value: Any):
        """Create a patcher for the mock value."""
        raise NotImplementedError


class CallableStrategy(PatchingStrategy):
    """Strategy for callable mock values."""
    
    def can_handle(self, mock_value: Any) -> bool:
        return callable(mock_value) and not isinstance(mock_value, (type, Mock))
        
    def create_patcher(self, target_path: str, mock_value: Any):
        return patch(target_path, side_effect=mock_value)


class MockObjectStrategy(PatchingStrategy):
    """Strategy for Mock and MagicMock objects."""
    
    def can_handle(self, mock_value: Any) -> bool:
        return isinstance(mock_value, (Mock, MagicMock))
        
    def create_patcher(self, target_path: str, mock_value: Any):
        return patch(target_path, mock_value)


class ValueStrategy(PatchingStrategy):
    """Strategy for direct value replacement."""
    
    def can_handle(self, mock_value: Any) -> bool:
        return True  # Default fallback strategy
        
    def create_patcher(self, target_path: str, mock_value: Any):
        return patch(target_path, mock_value)


class PropertyStrategy(PatchingStrategy):
    """Strategy for property mocking."""
    
    def can_handle(self, mock_value: Any) -> bool:
        return hasattr(mock_value, '__property_mock__')
        
    def create_patcher(self, target_path: str, mock_value: Any):
        return patch(target_path, new_callable=PropertyMock, return_value=mock_value)


class SmartPatcher:
    """Smart patcher that automatically selects the best strategy."""
    
    def __init__(self):
        self.strategies = [
            CallableStrategy(),
            MockObjectStrategy(),
            PropertyStrategy(),
            ValueStrategy()  # Keep as last (fallback)
        ]
        
    def create_patcher(self, target_path: str, mock_value: Any):
        """Create the most appropriate patcher for the mock value."""
        for strategy in self.strategies:
            if strategy.can_handle(mock_value):
                return strategy.create_patcher(target_path, mock_value)
        
        # Should never reach here due to ValueStrategy fallback
        raise ValueError(f"No strategy could handle mock value: {mock_value}")


# =============================================================================
# CONTEXT MANAGER FUNCTIONS
# =============================================================================

@contextmanager
def smart_mock(target_path: str, **kwargs):
    """Smart context manager for single module mocking."""
    context = SmartMockContext(target_path, **kwargs)
    with context:
        yield context


@contextmanager
def smart_patches(**module_configs):
    """Context manager for multiple module mocking."""
    contexts = {}
    active_contexts = []
    
    try:
        for module_path, config in module_configs.items():
            context = SmartMockContext(module_path, config)
            context.__enter__()
            contexts[module_path] = context
            active_contexts.append(context)
            
        yield contexts
        
    finally:
        for context in reversed(active_contexts):
            try:
                context.__exit__(None, None, None)
            except Exception:
                pass


# =============================================================================
# MOCK FACTORIES
# =============================================================================

class MockFactory:
    """Factory for creating common mock patterns."""
    
    @staticmethod
    def create_file_mock(content: str = "mock content", mode: str = "r"):
        """Create a file-like mock object."""
        from io import StringIO
        if 'b' in mode:
            from io import BytesIO
            return BytesIO(content.encode() if isinstance(content, str) else content)
        return StringIO(content)
        
    @staticmethod
    def create_response_mock(status_code: int = 200, json_data: Optional[Dict] = None, text: str = ""):
        """Create an HTTP response mock."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = text
        mock_response.json.return_value = json_data or {}
        mock_response.ok = status_code < 400
        return mock_response
        
    @staticmethod
    def create_database_mock(query_results: Optional[List] = None):
        """Create a database connection mock."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = query_results or [("test", "data")]
        mock_cursor.fetchone.return_value = (query_results or [("test", "data")])[0] if query_results else ("test", "data")
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.execute = Mock()
        mock_connection.commit = Mock()
        mock_connection.close = Mock()
        return mock_connection
        
    @staticmethod
    def create_class_mock(class_methods: Optional[Dict[str, Any]] = None, 
                         class_attributes: Optional[Dict[str, Any]] = None):
        """Create a mock class with specified methods and attributes."""
        class_methods = class_methods or {}
        class_attributes = class_attributes or {}
        
        class MockClass:
            def __init__(self, *args, **kwargs):
                for name, value in class_attributes.items():
                    setattr(self, name, value)
                    
        # Add methods to the class
        for method_name, behavior in class_methods.items():
            if callable(behavior):
                setattr(MockClass, method_name, lambda self, *args, **kwargs: behavior(*args, **kwargs))
            else:
                setattr(MockClass, method_name, lambda self, *args, **kwargs: behavior)
                
        return MockClass


# =============================================================================
# MOCK BUILDERS AND UTILITIES
# =============================================================================

class MockBuilder:
    """Builder pattern for creating complex mock configurations."""
    
    def __init__(self):
        self.config = {}
        
    def add_module(self, module_path: str, **attrs):
        """Add a module configuration."""
        self.config[module_path] = attrs
        return self
        
    def add_sys_mocks(self, argv: Optional[List[str]] = None, **kwargs):
        """Add sys module mocks."""
        from io import StringIO
        sys_config = {
            "argv": argv or ["test"],
            "stdout": StringIO(),
            "stderr": StringIO(),
            **kwargs
        }
        return self.add_module("sys", **sys_config)
        
    def add_os_mocks(self, environ: Optional[Dict[str, str]] = None, **kwargs):
        """Add os module mocks."""
        os_config = {
            "environ": environ or {"TEST": "true"},
            "getcwd": lambda: "/test/dir",
            **kwargs
        }
        return self.add_module("os", **os_config)
        
    def add_file_mocks(self, file_contents: Optional[Dict[str, str]] = None, **kwargs):
        """Add file operation mocks."""
        file_contents = file_contents or {"test.txt": "test content"}
        
        def mock_open(filename, mode='r', **open_kwargs):
            content = file_contents.get(filename, "default content")
            return MockFactory.create_file_mock(content, mode)
            
        builtins_config = {
            "open": mock_open,
            **kwargs
        }
        return self.add_module("builtins", **builtins_config)
        
    def add_network_mocks(self, responses: Optional[Dict[str, Dict]] = None, **kwargs):
        """Add network operation mocks."""
        responses = responses or {
            "GET": {"status_code": 200, "json_data": {"success": True}}
        }
        
        def mock_get(url, **req_kwargs):
            return MockFactory.create_response_mock(**responses.get("GET", {}))
            
        def mock_post(url, **req_kwargs):
            return MockFactory.create_response_mock(**responses.get("POST", {"status_code": 201}))
            
        requests_config = {
            "get": mock_get,
            "post": mock_post,
            **kwargs
        }
        return self.add_module("requests", **requests_config)
        
    def build(self) -> Dict[str, Any]:
        """Build the final configuration."""
        return self.config.copy()


def patch_object(obj: Any, attr_name: str, mock_value: Any):
    """Smart object patching utility."""
    patcher = SmartPatcher()
    full_path = f"{obj.__module__}.{obj.__class__.__name__}.{attr_name}"
    return patcher.create_patcher(full_path, mock_value)


def temporary_mock(target_path: str, mock_value: Any, duration: Optional[float] = None):
    """Create a temporary mock that auto-expires."""
    
    @contextmanager
    def temp_context():
        patcher = SmartPatcher().create_patcher(target_path, mock_value)
        mock_obj = patcher.start()
        
        def cleanup():
            try:
                patcher.stop()
            except Exception:
                pass
                
        if duration:
            timer = threading.Timer(duration, cleanup)
            timer.start()
            
        try:
            yield mock_obj
        finally:
            cleanup()
            
    return temp_context()


# =============================================================================
# MOCK INSPECTION AND DEBUGGING
# =============================================================================

class MockInspector:
    """Utility for inspecting and debugging mock configurations."""
    
    @staticmethod
    def inspect_context(context: SmartMockContext) -> Dict[str, Any]:
        """Inspect a mock context and return information about active mocks."""
        return {
            "target_path": context.target_path,
            "active_mocks": list(context.mock_registry.keys()),
            "mock_types": {name: type(mock).__name__ for name, mock in context.mock_registry.items()},
            "patch_count": len(context.active_patches)
        }
        
    @staticmethod
    def validate_mock_config(config: Dict[str, Any]) -> List[str]:
        """Validate a mock configuration and return any issues."""
        issues = []
        
        for module_path, module_config in config.items():
            if not isinstance(module_config, dict):
                issues.append(f"Module config for '{module_path}' must be a dictionary")
                continue
                
            # Try to import the module to validate it exists
            try:
                importlib.import_module(module_path)
            except ImportError:
                issues.append(f"Module '{module_path}' cannot be imported")
                
        return issues
        
    @staticmethod
    def analyze_mock_usage(context: SmartMockContext) -> Dict[str, Any]:
        """Analyze mock usage patterns in a context."""
        usage_stats = {
            "total_mocks": len(context.mock_registry),
            "mock_types": defaultdict(int),
            "call_counts": {},
            "unused_mocks": []
        }
        
        for name, mock_obj in context.mock_registry.items():
            mock_type = type(mock_obj).__name__
            usage_stats["mock_types"][mock_type] += 1
            
            if hasattr(mock_obj, 'call_count'):
                usage_stats["call_counts"][name] = mock_obj.call_count
                if mock_obj.call_count == 0:
                    usage_stats["unused_mocks"].append(name)
                    
        return dict(usage_stats)


# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================

# Legacy class names
MockContextManager = SmartMockContext
MethodPatcherStrategy = CallableStrategy
AttributePatcherStrategy = ValueStrategy
SmartPatcherStrategy = SmartPatcher

# Legacy function names
create_mock_class = MockFactory.create_class_mock

# Export commonly used items
__all__ = [
    # Core classes
    'SmartMockContext', 'SmartPatcher', 'MockFactory', 'MockBuilder',
    
    # Context managers
    'smart_mock', 'smart_patches', 'temporary_mock',
    
    # Utilities
    'patch_object', 'MockInspector',
    
    # Legacy compatibility
    'MockContextManager', 'create_mock_class'
]
