# Smart Mocking Framework

This is a robust and flexible mocking framework for Python unit and behavior tests. It is designed to be resilient to handle almost any type of input with minimal configuration, making your tests cleaner and more maintainable.

## Key Features

- **Type Detection**: Automatically detects the appropriate mocking strategy based on input type
- **Flexible API**: Simple, intuitive API for common mocking scenarios
- **Resilient Mocking**: Handles edge cases and complex object structures
- **Context Managers**: Clean setup and teardown with context manager pattern
- **Smart Patch Object**: Enhanced patching for attributes and methods
- **Mock Class Creation**: Easily create mock classes with predefined behaviors

## Basic Usage

### Smart Mocking with Context Manager

```python
from src.utils.test.smart_mock import smart_mock

# Mock multiple attributes/methods on a module with auto-detection
with smart_mock(
    "my_module",
    function=lambda x: x * 2,           # Mock a function
    value=42,                          # Mock a simple value
    config={"key": "value"},            # Mock a dictionary
    items=[1, 2, 3],                   # Mock a list
    class_obj=SomeClass                # Mock a class
) as mock_ctx:
    # Use the mocks
    result = my_module.function(5)     # Returns 10
    assert my_module.value == 42
    assert my_module.config["key"] == "value"
    assert my_module.items[0] == 1
```

### Patching Object Attributes

```python
from src.utils.test.smart_mock import patch_object

# Patch a method on an object
with patch_object(my_object, "method_name", lambda x: x * 3):
    result = my_object.method_name(5)  # Returns 15

# Patch an attribute
with patch_object(my_class, "attribute", "mocked value"):
    assert my_class.attribute == "mocked value"
```

### Creating Mock Classes

```python
from src.utils.test.smart_mock import create_mock_class

# Create a mock class with methods and attributes
MockDB = create_mock_class(
    class_methods={
        "query": lambda: [{"id": 1, "name": "Test"}],
        "connect": True,
        "execute": lambda x: f"Executed: {x}",
    },
    class_attributes={
        "connection_string": "mock://db",
        "is_connected": True,
    },
)

# Use the mock class
db = MockDB()
assert db.query() == [{"id": 1, "name": "Test"}]
assert db.connection_string == "mock://db"
```

## Advanced Usage

### Dynamic Mock Addition

```python
with smart_mock("my_module") as mock_ctx:
    # Start with no mocks
    
    # Add mocks dynamically during the test
    mock_ctx.add_mock("new_function", lambda x: x ** 2)
    result = my_module.new_function(4)  # Returns 16
    
    # Update an existing mock
    mock_ctx.add_mock("new_function", "replaced")
    assert my_module.new_function == "replaced"
```

### Temporarily Updating Mocks

```python
with smart_mock("os", path_exists=True) as mock_ctx:
    assert os.path_exists("some_file") is True
    
    # Temporarily change the behavior
    with mock_ctx.update_patch("path_exists", False):
        assert os.path_exists("some_file") is False
    
    # Back to original behavior
    assert os.path_exists("some_file") is True
```

## Using in Test Fixtures

The smart mocking framework integrates seamlessly with pytest fixtures:

```python
@pytest.fixture
def mock_database():
    with smart_mock(
        "app.database",
        connect=lambda: True,
        query=lambda sql: [{"id": 1}] if "SELECT" in sql else [],
        close=None
    ) as mock_ctx:
        yield mock_ctx

def test_database_query(mock_database):
    result = app.database.query("SELECT * FROM users")
    assert len(result) == 1
    assert result[0]["id"] == 1
```

## Implementation Details

This framework uses several strategies under the hood to handle different types of mocks:

1. **SmartPatcherStrategy**: Automatically detects the best strategy based on input type
2. **MethodPatcherStrategy**: For mocking callable methods
3. **AttributePatcherStrategy**: For mocking simple attributes
4. **MappingPatcherStrategy**: For mocking dictionary-like objects
5. **ClassPatcherStrategy**: For mocking classes

All of these strategies follow the strategy pattern, implementing a common interface defined by `AbstractStrategy`.
