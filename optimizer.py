from static_analysis import StaticAnalyzer
from dynamic_profiler import DynamicProfiler
from refactoring_engine import RefactoringEngine
from report_generator import generate_html_report
import ast
import astor

class PythonOptimizer:
    def __init__(self, script_path):
        self.script_path = script_path

    def format_suggestions(self, suggestions):
        """Clean and simplify suggestions for better readability."""
        formatted = []
        for suggestion in suggestions:
            if "BinOp" in suggestion:
                # Parse and simplify BinOp suggestions
                formatted.append(
                    suggestion
                    .replace("Expression (", "")
                    .replace("Call(func=", "Function ")
                    .replace("Attribute(value=", "")
                    .replace("args=[", " with arguments ")
                    .replace("keywords=", "")
                    .replace("op=", "operation ")
                    .replace("ctx=Load()", "")
                    .replace("ctx=Store()", "")
                    .replace(", ", ", ")
                    .replace(", slice=", " and index ")
                    .replace(", attr=", " accessing ")
                    .replace("math,", "math")
                    .replace("BinOp(", "Operation (")
                    .replace(")", "")
                    .replace("Constant(value=", "value ")
                )
            else:
                # Keep other suggestions as is
                formatted.append(suggestion)
        return formatted

    def optimize(self):
        # Load source code
        with open(self.script_path, "r") as file:
            source_code = file.read()

        # Perform static analysis
        static_analyzer = StaticAnalyzer()
        static_results = static_analyzer.analyze(source_code)

        # Perform dynamic profiling
        profiler = DynamicProfiler(self.script_path)
        runtime_profile = profiler.profile_runtime()
        memory_profile = profiler.profile_memory()

        # Refactor code (optional, not currently applied to output)
        tree = ast.parse(source_code)
        refactorer = RefactoringEngine()
        optimized_tree = refactorer.visit(tree)
        optimized_code = astor.to_source(optimized_tree)

        # Combine results
        static_suggestions = (
            static_results["high_iterations"]
            + static_results["repeated_computations"]
            + static_results["vectorization_candidates"]
        )
        formatted_static_suggestions = self.format_suggestions(static_suggestions)

        # Generate HTML report
        report = generate_html_report(
            formatted_static_suggestions, 
            runtime_profile + "\n" + memory_profile
        )

        # Save the report
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
