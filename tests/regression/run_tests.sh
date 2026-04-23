#!/bin/bash

# Regression Test Runner

echo "=========================================="
echo "Running Regression Tests"
echo "=========================================="

# Activate virtual environment if it exists
if [ -d "../../venv" ]; then
    source ../../venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the regression tests
python test_regression.py

# Capture exit code
EXIT_CODE=$?

# Show result
if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
else
    echo ""
    echo "❌ Some tests failed!"
fi

exit $EXIT_CODE