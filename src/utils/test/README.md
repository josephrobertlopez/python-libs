# Smart Mocking Framework & Annotation System

This is a comprehensive smart mocking framework for Python unit and behavior tests, featuring both traditional context managers and modern annotation-based patterns. It's designed to dramatically reduce test boilerplate while providing flexible, resilient mocking capabilities.

## 🎯 Key Features

- **Smart Annotation Decorators**: Dramatically reduce boilerplate with declarative test decorators
- **Shared Configuration System**: Centralized, reusable mock configurations
- **Type Detection**: Automatically detects appropriate mocking strategies
- **Context Composition**: Combine multiple mocks into single, elegant contexts
- **Flexible API**: Simple, intuitive API for common mocking scenarios
- **Resilient Mocking**: Handles edge cases and complex object structures
- **Clean Teardown**: Automatic cleanup with context manager patterns

## 🚀 Quick Start: Modern Annotation Patterns

### Basic Test Decorators

```python
from tests.shared_annotations import (
    runner_test, audio_test, file_system_test, 
    output_test, StandardTestCase
)

class TestMyModule(StandardTestCase):
    """Use StandardTestCase for enhanced testing capabilities."""

    @runner_test(argv=["program", "--name", "Alice"])
    @output_test()
    def test_simple_runner(self, **kwargs):
        """Test with system arguments and output capture."""
        run_my_program()
        assert "Hello Alice" in kwargs['captured_stdout']

    @audio_test()
    def test_audio_functionality(self):
        """Test with automatic pygame mocking."""
        play_sound("test.wav")  # pygame automatically mocked

    @file_system_test(
        files_exist={"/config.txt": True, "/missing.txt": False},
        file_contents={"/config.txt": "config_data"}
    )
    def test_file_operations(self):
        """Test with file system mocking."""
        with open("/config.txt") as f:
            assert f.read() == "config_data"
```

### Pre-configured Module Decorators

```python
from tests.shared_annotations import (
    mock_test_sys, mock_test_os, mock_test_builtins,
    mock_test_logging, mock_test_pygame
)

class TestEnvironment(StandardTestCase):
    
    @mock_test_sys(argv=["test", "--flag"], frozen=True)
    def test_system_args(self):
        """System module pre-configured with common settings."""
        import sys
        assert sys.argv == ["test", "--flag"]
        assert sys.frozen == True

    @mock_test_os(environ={"TEST_VAR": "value"})
    def test_environment_vars(self):
        """OS module with environment variables."""
        import os
        assert os.environ["TEST_VAR"] == "value"

    @mock_test_builtins(open=custom_open_mock)
    def test_builtin_functions(self):
        """Mock built-in functions like open, print."""
        with open("test.txt") as f:
            # Your custom_open_mock behavior
            pass
```

### Context Composition for Complex Scenarios

```python
from tests.shared_annotations import (
    mock_runner_context, mock_audio_context, mock_logging_context
)

def test_complex_integration():
    """Compose multiple contexts for complex scenarios."""
    with mock_runner_context(
        sys={"argv": ["program", "--verbose"]},
        os={"environ": {"DEBUG": "1"}},
        override_logging=True
    ):
        # All runner-related mocks active
        run_complex_program()

def test_audio_with_custom_config():
    """Use audio context with custom overrides."""
    with mock_audio_context(
        pygame_overrides={"mixer.get_init": lambda: (44100, -16, 2)}
    ):
        # Enhanced audio testing
        initialize_audio_system()
```

## 📊 Boilerplate Reduction Examples

### Before: Manual Context Managers (Verbose)

```python
# ❌ OLD WAY: 15+ lines of setup
def test_complex_scenario():
    from io import StringIO
    from unittest.mock import Mock
    
    with smart_mock("os", environ={"TEST_VAR": "value"}):
        with smart_mock("sys", argv=["test", "--flag"], stdout=StringIO()):
            with smart_mock("builtins", open=Mock(), print=Mock()):
                with smart_mock("logging", getLogger=Mock()):
                    # Finally, your test logic
                    run_test()
                    assert condition
```

### After: Smart Annotations (Clean)

```python
# ✅ NEW WAY: 3 lines total!
@runner_test(argv=["test", "--flag"])
@output_test()
def test_complex_scenario(**kwargs):
    run_test()
    assert "expected" in kwargs['captured_stdout']
```

**Result: 80% reduction in boilerplate code!**

## 🏗️ Architecture & Components

### Core Annotation System

```python
# Individual module decorators
@mock_test_sys(argv=["test"], frozen=True)
@mock_test_os(environ={"VAR": "value"})
@mock_test_builtins(open=custom_mock)
@mock_test_logging(getLogger=Mock())
@mock_test_pygame()  # Pre-configured pygame mocking

# Specialized decorators
@mock_output(stdout_capture=True, stderr_capture=True)
@mock_env_vars(TEST_VAR="value", DEBUG="1")
@mock_file_system(files_exist={"/file.txt": True})
```

### Context Composition Functions

```python
# Composed contexts for common scenarios
mock_runner_context(sys={}, os={}, override_logging=False)
mock_audio_context(pygame_overrides={})
mock_logging_context(config_overrides={})

# Usage
with mock_runner_context(
    sys={"argv": ["custom", "args"]},
    os={"environ": {"CUSTOM_VAR": "value"}}
):
    # Context automatically handles all runner-related mocking
    pass
```

### Enhanced Base Classes

```python
class StandardTestCase(SmartMockTestCase):
    """Enhanced base class with additional helper methods."""
    
    def setUp(self):
        """Common setup for all tests."""
        super().setUp()
        # Additional setup
    
    def assert_output_contains(self, text, output):
        """Helper for output assertions."""
        self.assertIn(text, output)
    
    def create_temp_file(self, content):
        """Helper for file testing."""
        # Implementation
```

## 🎨 Advanced Patterns

### Stacked Decorators for Complex Scenarios

```python
@runner_test(argv=["program", "--config", "test.conf"])
@audio_test()
@file_system_test(files_exist={"/test.conf": True})
@output_test()
def test_full_integration(**kwargs):
    """Multiple decorators stack cleanly."""
    run_program_with_audio_and_config()
    assert "Audio initialized" in kwargs['captured_stdout']
```

### Parametrized Tests with Shared Configurations

```python
from tests.shared_annotations import create_runner_test_cases

@pytest.mark.parametrize("args, expected", create_runner_test_cases())
def test_various_scenarios(args, expected):
    """Parametrized tests with shared test case generation."""
    
    @runner_test(argv=["program"] + args)
    @output_test()
    def run_test(**kwargs):
        run_program(*args)
        assert expected in kwargs['captured_stdout']
    
    run_test()
```

### Custom Decorator Creation

```python
from functools import partial
from tests.shared_annotations import mock_test_module

# Create custom pre-configured decorators
mock_test_requests = partial(
    mock_test_module,
    "requests",
    get=Mock(return_value=Mock(status_code=200)),
    post=Mock(return_value=Mock(status_code=201))
)

@mock_test_requests()
def test_api_calls():
    """Use custom decorator for API testing."""
    response = requests.get("http://example.com")
    assert response.status_code == 200
```

## 🎯 Best Practices

### 1. Use Appropriate Abstraction Level

```python
# ✅ GOOD: Use high-level decorators for common scenarios
@runner_test(argv=["program", "--flag"])
def test_runner():
    pass

# ⚠️ OKAY: Use module decorators for specific needs
@mock_test_sys(argv=["program", "--flag"])
def test_specific():
    pass

# ❌ AVOID: Manual context managers for simple cases
def test_manual():
    with smart_mock("sys", argv=["program", "--flag"]):
        pass
```

### 2. Choose the Right Base Class

```python
# ✅ GOOD: Use StandardTestCase for comprehensive testing
class TestMyFeature(StandardTestCase):
    @runner_test(argv=["test"])
    def test_functionality(self):
        pass

# ✅ GOOD: Use StandardPytestBase for pytest-style tests
class TestMyFeature(StandardPytestBase):
    @audio_test()
    def test_audio_functionality(self):
        pass
```

### 3. Leverage Preset Configurations

```python
# ✅ GOOD: Use presets for common patterns
@runtime_mock("cli_app", argv=["myapp", "--verbose"])
def test_cli_functionality():
    pass

# ✅ GOOD: Extend presets with additional overrides
@runtime_mock("audio", pygame={"mixer": {"custom_setting": True}})
def test_audio_with_custom_settings():
    pass
```

### 4. Organize Tests with StandardTestCase
```python
class TestMyFeature(StandardTestCase):
    """Group related tests and inherit helpful methods."""
    
    def setUp(self):
        """Common setup for all tests in this class."""
        super().setUp()
        self.common_data = "shared_value"
    
    @runner_test(argv=["program"])
    def test_feature_one(self):
        # Use self.common_data
        pass
    
    @audio_test()
    def test_feature_two(self):
        # Inherits all StandardTestCase helpers
        pass
```

### 5. Create Custom Decorators for Domain-Specific Testing

```python
# Define once, use everywhere
from functools import partial

database_test = partial(
    mock_test_module,
    "app.database",
    connect=Mock(return_value=True),
    query=Mock(return_value=[{"id": 1}])
)

# Use in multiple tests
@database_test()
def test_user_creation():
    create_user("test")

@database_test()
def test_user_query():
    find_user(1)
```

### 6. Prefer Composition for Complex Scenarios

```python
# ✅ GOOD: Use composed contexts
def test_complex():
    with mock_runner_context(
        sys={"argv": ["program", "--config", "test.conf"]},
        os={"environ": {"DEBUG": "1"}}
    ):
        run_integration_test()

# ❌ AVOID: Many stacked decorators
@mock_test_sys(argv=["program", "--config", "test.conf"])
@mock_test_os(environ={"DEBUG": "1"})
@mock_test_builtins(open=Mock())
@mock_test_logging(getLogger=Mock())
# ... too many decorators become hard to read
```

## 🚨 Common Pitfalls & Solutions

### 1. Import Order Issues

```python
# ❌ PROBLEM: Import conflicts
from unittest.mock import Mock
from tests.shared_annotations import mock_test_sys
import sys  # This can conflict with mocking

# ✅ SOLUTION: Import mocked modules inside test functions
@mock_test_sys(argv=["test"])
def test_import_correctly():
    import sys  # Import after decorator is applied
    assert sys.argv == ["test"]
```

### 2. Mock Scope and Cleanup

```python
# ✅ GOOD: Decorators handle cleanup automatically
@mock_test_sys(argv=["test"])
def test_automatic_cleanup():
    import sys
    assert sys.argv == ["test"]
# sys.argv automatically restored after test

# ⚠️ BE CAREFUL: Manual context managers require proper nesting
def test_manual_cleanup():
    with smart_mock("sys", argv=["test"]):
        # Mocks active here
        pass
    # Mocks cleaned up here
```

### 3. Sharing State Between Tests

```python
# ❌ AVOID: Shared mutable state
shared_mock = Mock()

@mock_test_module("requests", get=shared_mock)
def test_one():
    pass

@mock_test_module("requests", get=shared_mock)
def test_two():
    # shared_mock may have unexpected call history
    pass

# ✅ GOOD: Fresh mocks for each test
@mock_test_module("requests", get=Mock())
def test_one():
    pass

@mock_test_module("requests", get=Mock())
def test_two():
    pass
```

## 🔍 Implementation Details

This framework uses several strategies to handle different types of mocks:

1. **SmartPatcherStrategy**: Automatically detects the best strategy based on input type
2. **MethodPatcherStrategy**: For mocking callable methods
3. **AttributePatcherStrategy**: For mocking simple attributes
4. **MappingPatcherStrategy**: For mocking dictionary-like objects
5. **ClassPatcherStrategy**: For mocking classes

All strategies follow the strategy pattern, implementing a common interface defined by `AbstractStrategy`.

## 📚 Additional Resources

- **Traditional API**: Use `smart_mock`, `patch_object`, `create_mock_class` for dynamic scenarios
- **Modern API**: Use decorators from `tests.shared_annotations` for declarative testing
- **Base Classes**: Extend `StandardTestCase` for enhanced testing capabilities
- **Context Composition**: Use `mock_*_context` functions for complex scenarios

## 🎉 Summary

This smart mocking framework provides:
- **80% reduction** in test boilerplate code
- **Consistent patterns** across your entire test suite
- **Easy customization** for domain-specific needs
- **Gradual migration** path from legacy patterns
- **Enhanced maintainability** through centralized configurations

Choose the right tool for each scenario:
- **Decorators** for most common cases
- **Context managers** for dynamic behavior
- **Composition functions** for complex scenarios
- **Base classes** for shared functionality
