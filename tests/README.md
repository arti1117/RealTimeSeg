# Test Suite

Validation tests for the RealTimeSeg project.

## Available Tests

### WebSocket Error Handling Validation
**File**: `test_websocket_fixes.py`
**Purpose**: Validates that WebSocket error handlers properly handle connection disconnects
**Type**: Static code analysis

**Run**:
```bash
python tests/test_websocket_fixes.py
```

**What it Tests**:
- ✅ Required imports (WebSocketDisconnect, Starlette)
- ✅ Error handler protection in all WebSocket message handlers
- ✅ WebSocket close call protection
- ✅ Proper exception type coverage
- ✅ Python syntax validation

**Expected Output**:
```
✓ All tests passed!

WebSocket error handling is properly implemented:
  • All error handlers have disconnect protection
  • websocket.close() calls are wrapped in try/except
  • Proper exception types are caught
  • No syntax errors
```

## Test Results

Last test run: 2025-10-28
Status: ✅ ALL TESTS PASSED (5/5)

See [WEBSOCKET_TEST_REPORT.md](../docs/WEBSOCKET_TEST_REPORT.md) for detailed results.

## Future Tests

Planned test additions:
- [ ] Integration tests for WebSocket connections
- [ ] Model loading and inference tests
- [ ] Frame processing pipeline tests
- [ ] Visualization rendering tests
- [ ] End-to-end browser tests (Playwright)

## Running All Tests

Currently only one test suite exists:
```bash
python tests/test_websocket_fixes.py
```

When more tests are added:
```bash
# Run all Python tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=backend --cov-report=html
```

## Test Development Guidelines

### Structure
- Place test files in `tests/` directory
- Name test files: `test_<feature>.py`
- Use descriptive test function names

### Standards
- Include docstrings explaining what is tested
- Use clear pass/fail indicators
- Provide actionable error messages
- Generate detailed reports for failures

### Best Practices
- Test one feature per file
- Keep tests fast (< 1 second per test)
- Make tests deterministic (no randomness)
- Document expected behavior clearly
