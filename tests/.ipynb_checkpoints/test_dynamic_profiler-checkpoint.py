import os
import sys
import io
from unittest.mock import patch, mock_open
import pytest

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.dynamic_profiler import DynamicProfiler

@pytest.fixture
def example_script(tmp_path):
    """
    Fixture to create a temporary Python script for testing.
    """
    script_content = """
import time

def test_function():
    time.sleep(1)
    arr = [i for i in range(1000)]
    print(sum(arr))

if __name__ == "__main__":
    test_function()
"""
    script_path = tmp_path / "example_script.py"
    with open(script_path, "w") as script_file:
        script_file.write(script_content)
    return str(script_path)


def test_profile_runtime(example_script):
    """
    Test that DynamicProfiler correctly profiles runtime performance.
    """
    profiler = DynamicProfiler(example_script)
    result = profiler.profile_runtime()

    # Assert runtime profiling produces expected output
    assert "test_function" in result or "function calls" in result, "Runtime profiling failed to capture function execution"
    assert "cumtime" in result, "Cumulative time not reported in profiling output"


@patch("memory_profiler.memory_usage", return_value=[10.5, 15.3])
def test_mocked_memory_profiling(mock_memory_usage):
    """
    Test memory profiling with mocked memory usage.
    """
    profiler = DynamicProfiler("mock_script.py")
    mock_script_content = "print('Mock script executed')"
    with patch("builtins.open", mock_open(read_data=mock_script_content)):
        result = profiler.profile_memory()
    assert "Peak memory usage: 15.30 MB" in result, "Mocked memory profiling failed"

