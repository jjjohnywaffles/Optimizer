import sys
import os
import pytest  # Optional but recommended for cleaner test management

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.static_analysis import StaticAnalyzer


def test_static_analysis():
    """
    Test the StaticAnalyzer class to ensure it correctly identifies
    high iteration loops, repeated computations, and nested loops.
    """
    # Example Python code to analyze
    code = """
for i in range(100000):
    x = (i + 1) * (i + 2)
for i in range(10):
    for j in range(10):
        print(i, j)
"""

    # Initialize StaticAnalyzer
    analyzer = StaticAnalyzer()

    # Perform analysis
    results = analyzer.analyze(code)

    # Assert results is a dictionary with expected keys
    assert isinstance(results, dict), "Results should be a dictionary"
    assert all(key in results for key in ["high_iterations", "repeated_computations", "nested_loops", "vectorization_candidates"]), \
        "Results missing expected keys"

    # Assert high iteration loop is detected
    assert len(results["high_iterations"]) > 0, "Failed to detect high iteration loops"

    # Assert repeated computations are detected
    assert len(results["repeated_computations"]) > 0, "Failed to detect repeated computations"

    # Assert nested loops are detected
    assert len(results["nested_loops"]) > 0, "Failed to detect nested loops"


if __name__ == "__main__":
    pytest.main()
