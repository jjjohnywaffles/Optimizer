from static_analysis import StaticAnalyzer
from dynamic_profiler import DynamicProfiler
from refactoring_engine import RefactoringEngine
from report_generator import generate_html_report
import ast
import astor

class PythonOptimizer:
    def __init__(self, script_path):
        self.script_path = script_path

    def optimize(self):
        # Static Analysis
        with open(self.script_path, "r") as file:
            source_code = file.read()

        static_analyzer = StaticAnalyzer()
        static_results = static_analyzer.analyze(source_code)

        # Dynamic Profiling
        profiler = DynamicProfiler(self.script_path)
        runtime_profile = profiler.profile_runtime()
        memory_profile = profiler.profile_memory()

        # Refactor Code
        tree = ast.parse(source_code)
        refactorer = RefactoringEngine()
        optimized_tree = refactorer.visit(tree)
        optimized_code = astor.to_source(optimized_tree)

        # Generate Report
        static_suggestions = (
            static_results["high_iterations"]
            + static_results["repeated_computations"]
            + static_results["vectorization_candidates"]
        )
        report = generate_html_report(static_suggestions, runtime_profile + "\n" + memory_profile)

        with open("report.html", "w") as report_file:
            report_file.write(report)

        print("Optimization complete. Report saved as 'report.html'.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Python Code Optimizer")
    parser.add_argument("script", help="Path to the Python script to analyze.")
    args = parser.parse_args()

    optimizer = PythonOptimizer(args.script)
    optimizer.optimize()
