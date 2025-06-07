def method_called_in_mock(mock, method, *args):
    # Get all method calls for the specified method name
    method_calls = [m for m in mock.method_calls if m[0] == method]

    # If no matching method calls found, print debug info and return False
    if len(method_calls) == 0:
        print(f"method call of {method} not found on mock")
        print(f"Available method calls: {[m[0] for m in mock.method_calls]}")
        return False

    # Check if any of the method calls match the given arguments
    for m in method_calls:
        # Compare arguments
        if m.args == args:
            print(f"method {method} called with args")
            return True

    # If we reached here, the method was called but with different args
    print(f"method {method} not called with args")
    print(f"Expected args: {args}")
    print(f"Actual calls: {[(m[0], m.args) for m in method_calls]}")
    return False
