import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from static_analysis import StaticAnalyzer

def test_static_analysis():
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
    
    # Assert high iteration loop is detected
    assert len(results["high_iterations"]) > 0, "Failed to detect high iteration loops"
    
    # Assert repeated computations are detected
    assert len(results["repeated_computations"]) > 0, "Failed to detect repeated computations"
    
    # Assert nested loops are detected
    assert results["nested_loops"] > 0, "Failed to detect nested loops"
