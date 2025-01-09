from utils.static_analysis import StaticAnalyzer
from utils.dynamic_profiler import DynamicProfiler
from utils.refactoring_engine import RefactoringEngine
from utils.report_generator import generate_html_report
import ast
import astor
import os

class PythonOptimizer:
    def __init__(self, script_path):
        self.script_path = script_path

    def format_suggestions(self, suggestions):
        """Clean and simplify suggestions for better readability."""
        def simplify_ast_expression(expression):
            """Simplify an AST expression into plain English."""
            if "Call" in expression:
                return "a function call"
            if "BinOp" in expression:
                return "a mathematical operation"
            if "Subscript" in expression:
                return "a matrix or array element"
            return expression

        formatted = []
        for suggestion in suggestions:
            if "BinOp" in suggestion or "Call" in suggestion or "Subscript" in suggestion:
                # Simplify the AST structure
                readable = simplify_ast_expression(suggestion)
                formatted.append(f"{suggestion.split(':')[0]}: Consider caching {readable}.")
            else:
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

        # Refactor code and save the output in the "optimized_code" folder
        tree = ast.parse(source_code)
        refactorer = RefactoringEngine()
        optimized_tree = refactorer.visit(tree)
        optimized_code = astor.to_source(optimized_tree)
        
        # Create the "optimized_code" folder if it doesn't exist
        output_folder = "optimized_code"
        os.makedirs(output_folder, exist_ok=True)

        # Save the optimized code to a new file inside the folder
        script_name = os.path.basename(self.script_path).replace(".py", "_optimized.py")
        optimized_file_path = os.path.join(output_folder, script_name)
        with open(optimized_file_path, "w") as optimized_file:
            optimized_file.write(optimized_code)

        print(f"Optimized code saved to '{optimized_file_path}'.")

        # Combine results
        static_suggestions = (
            static_results["high_iterations"]
            + static_results["repeated_computations"]
            + static_results["vectorization_candidates"]
        )
        nested_loop_suggestions = [
            {"line": loop["line"], "level": loop["level"], "suggestion": "Consider reducing nesting."}
            for loop in static_results["nested_loops"]
        ]


        # Generate HTML report
        formatted_static_suggestions = self.format_suggestions(static_suggestions)
        report = generate_html_report(
            formatted_static_suggestions, nested_loop_suggestions, runtime_profile + "\n" + memory_profile
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
