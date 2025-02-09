def method_called_in_mock(mock, method, *args):
    method_calls = [m for m in mock.method_calls if m[0] == method]
    if len(method_calls) == 0:
        print(f"method call of {method} not found on mock")
        return False
    for m in method_calls:
        if m.args == args:
            print(f"method {method} called with args")
            return True
    print(f"method {method} not called with args")
    return False
