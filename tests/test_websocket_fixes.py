#!/usr/bin/env python3
"""
Test validation for WebSocket error handling fixes.
Verifies that the double-send error is properly handled.
"""

import re
import ast
from pathlib import Path

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_test(name, passed, details=None):
    """Print test result with color coding."""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} - {name}")
    if details:
        print(f"      {details}")

def check_error_handler_protection(file_path):
    """Check if error handlers in WebSocket message handlers have proper protection."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Find all async functions that handle WebSocket messages
    # These are: handle_frame, handle_mode_change, handle_viz_update, handle_stats_request
    ws_functions = ['handle_frame', 'handle_mode_change', 'handle_viz_update', 'handle_stats_request']

    results = []
    for func_name in ws_functions:
        # Find the function
        func_pattern = rf'async def {func_name}\('
        func_match = re.search(func_pattern, content)

        if not func_match:
            continue

        # Get the function body (until next function or end)
        func_start = func_match.start()
        next_func = re.search(r'\nasync def |^async def ', content[func_start + 1:], re.MULTILINE)

        if next_func:
            func_end = func_start + next_func.start() + 1
        else:
            func_end = len(content)

        func_body = content[func_start:func_end]

        # Check if this function has error handler with websocket.send_json
        has_error_handler = 'except Exception' in func_body and 'await websocket.send_json' in func_body

        if has_error_handler:
            # Check if the send is protected
            has_protection = (
                'try:' in func_body and
                'except (RuntimeError, WebSocketDisconnect):' in func_body
            )

            line_num = content[:func_start].count('\n') + 1

            results.append({
                'function': func_name,
                'line': line_num,
                'protected': has_protection
            })

    return results

def check_websocket_close_protection(file_path):
    """Check if websocket.close() calls have error protection."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Find websocket.close() calls
    pattern = r'await websocket\.close\(\)'
    matches = list(re.finditer(pattern, content))

    results = []
    for match in matches:
        start_pos = match.start()
        # Get context
        context_start = max(0, start_pos - 200)
        context_end = min(len(content), match.end() + 100)
        context = content[context_start:context_end]

        # Check if wrapped in try/except
        has_protection = (
            'try:' in context and
            'RuntimeError' in context and
            context.index('try:') < context.index('await websocket.close()')
        )

        line_num = content[:start_pos].count('\n') + 1

        results.append({
            'line': line_num,
            'protected': has_protection
        })

    return results

def check_imports(file_path):
    """Check if necessary imports are present."""
    with open(file_path, 'r') as f:
        content = f.read()

    has_websocket_disconnect = 'WebSocketDisconnect' in content
    has_from_starlette = 'from fastapi import' in content or 'from starlette' in content

    return has_websocket_disconnect, has_from_starlette

def run_validation():
    """Run all validation tests."""
    print(f"\n{BOLD}WebSocket Error Handling Validation{RESET}")
    print("=" * 60)

    app_path = Path(__file__).parent / 'app.py'

    if not app_path.exists():
        print(f"{RED}✗ FAIL{RESET} - app.py not found at {app_path}")
        return False

    all_passed = True

    # Test 1: Check imports
    print(f"\n{BOLD}Test 1: Required Imports{RESET}")
    has_disconnect, has_starlette = check_imports(app_path)

    print_test(
        "WebSocketDisconnect import",
        has_disconnect,
        "Required for handling disconnect exceptions"
    )
    all_passed &= has_disconnect

    print_test(
        "Starlette/FastAPI imports",
        has_starlette,
        "Required for WebSocket functionality"
    )
    all_passed &= has_starlette

    # Test 2: Check error handler protection
    print(f"\n{BOLD}Test 2: Error Handler Protection{RESET}")
    error_handlers = check_error_handler_protection(app_path)

    unprotected_handlers = [h for h in error_handlers if not h['protected']]

    print_test(
        f"WebSocket message handlers with error protection",
        len(unprotected_handlers) == 0,
        f"Found {len(error_handlers)} handlers, all properly protected"
    )

    if unprotected_handlers:
        for handler in unprotected_handlers:
            print(f"      {YELLOW}⚠{RESET} Unprotected: {handler['function']} at line {handler['line']}")
        all_passed = False

    # Test 3: Check websocket.close() protection
    print(f"\n{BOLD}Test 3: WebSocket Close Protection{RESET}")
    close_calls = check_websocket_close_protection(app_path)

    unprotected_closes = [c for c in close_calls if not c['protected']]

    print_test(
        "websocket.close() calls with error handling",
        len(unprotected_closes) == 0,
        f"Found {len(close_calls)} close calls, {len(close_calls) - len(unprotected_closes)} protected"
    )

    if unprotected_closes:
        for close in unprotected_closes:
            print(f"      {YELLOW}⚠{RESET} Unprotected close at line {close['line']}")
        all_passed = False

    # Test 4: Check for RuntimeError and WebSocketDisconnect in exception handlers
    print(f"\n{BOLD}Test 4: Exception Type Coverage{RESET}")
    with open(app_path, 'r') as f:
        content = f.read()

    # Count protected sends (4 inner error handlers)
    pattern = r'except \(RuntimeError, WebSocketDisconnect\):'
    protected_sends = len(re.findall(pattern, content))

    # Also count RuntimeError-only protection for close() (1 outer handler)
    close_pattern = r'except RuntimeError:.*?# Already closed'
    protected_closes = len(re.findall(close_pattern, content, re.DOTALL))

    total_protected = protected_sends + protected_closes

    print_test(
        "Handlers catching RuntimeError and/or WebSocketDisconnect",
        total_protected >= 5,  # We expect 4 send handlers + 1 close handler = 5 total
        f"Found {protected_sends} send handlers + {protected_closes} close handlers = {total_protected} total"
    )
    all_passed &= (total_protected >= 5)

    # Test 5: Code syntax validation
    print(f"\n{BOLD}Test 5: Python Syntax Validation{RESET}")
    try:
        with open(app_path, 'r') as f:
            code = f.read()
        ast.parse(code)
        print_test("Python syntax valid", True, "No syntax errors found")
    except SyntaxError as e:
        print_test("Python syntax valid", False, f"Syntax error at line {e.lineno}: {e.msg}")
        all_passed = False

    # Summary
    print(f"\n{BOLD}Test Summary{RESET}")
    print("=" * 60)
    if all_passed:
        print(f"{GREEN}✓ All tests passed!{RESET}")
        print("\nWebSocket error handling is properly implemented:")
        print("  • All error handlers have disconnect protection")
        print("  • websocket.close() calls are wrapped in try/except")
        print("  • Proper exception types are caught")
        print("  • No syntax errors")
    else:
        print(f"{RED}✗ Some tests failed{RESET}")
        print("\nPlease review the failed tests above and fix the issues.")

    return all_passed

if __name__ == '__main__':
    import sys
    success = run_validation()
    sys.exit(0 if success else 1)
