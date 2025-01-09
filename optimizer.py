from utils.static_analysis import StaticAnalyzer
from utils.dynamic_profiler import DynamicProfiler
from utils.refactoring_engine import RefactoringEngine
from utils.report_generator import generate_html_report
import ast
import astor
import os

class PythonOptimizer:
    """
    Main class for optimizing Python scripts by analyzing, profiling, and refactoring code.
    Generates a report and an optimized version of the script.
    """
    def __init__(self, script_path):
        """
        Initialize the optimizer with the path to the script to be optimized.

        Args:
            script_path (str): Path to the Python script to analyze and optimize.
        """
        self.script_path = script_path

    def format_suggestions(self, suggestions):
        """
        Format static analysis suggestions for better readability.

        Args:
            suggestions (list): List of raw suggestions from static analysis.

        Returns:
            list: List of formatted suggestions with simplified descriptions.
        """
        def simplify_ast_expression(expression):
            """
            Simplify complex AST-based suggestions into plain English descriptions.

            Args:
                expression (str): The AST expression or suggestion string.

            Returns:
                str: Simplified description of the suggestion.
            """
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
                # Translate technical AST suggestion into plain English
                readable = simplify_ast_expression(suggestion)
                formatted.append(f"{suggestion.split(':')[0]}: Consider caching {readable}.")
            else:
                formatted.append(suggestion)
        return formatted

    def optimize(self):
        """
        Perform the optimization process:
        1. Static analysis to identify inefficiencies.
        2. Dynamic profiling for runtime and memory usage.
        3. Refactoring code for optimization.
        4. Generating and saving a detailed report and optimized script.
        """
        # Load source code from the provided script path
        with open(self.script_path, "r") as file:
            source_code = file.read()

        # Perform static analysis to identify inefficiencies
        static_analyzer = StaticAnalyzer()
        static_results = static_analyzer.analyze(source_code)

        # Perform dynamic profiling to measure runtime and memory usage
        profiler = DynamicProfiler(self.script_path)
        runtime_profile = profiler.profile_runtime()
        memory_profile = profiler.profile_memory()

        # Parse the source code into an Abstract Syntax Tree (AST)
        tree = ast.parse(source_code)

        # Refactor the AST using the RefactoringEngine to optimize the code
        refactorer = RefactoringEngine()
        optimized_tree = refactorer.visit(tree)

        # Convert the optimized AST back into Python source code
        optimized_code = astor.to_source(optimized_tree)

        # Ensure the "optimized_code" directory exists
        output_folder = "optimized_code"
        os.makedirs(output_folder, exist_ok=True)

        # Save the optimized code to a new file in the "optimized_code" folder
        script_name = os.path.basename(self.script_path).replace(".py", "_optimized.py")
        optimized_file_path = os.path.join(output_folder, script_name)
        with open(optimized_file_path, "w") as optimized_file:
            optimized_file.write(optimized_code)

        print(f"Optimized code saved to '{optimized_file_path}'.")

        # Combine results from static analysis into a single list
        static_suggestions = (
            static_results["high_iterations"]
            + static_results["repeated_computations"]
            + static_results["vectorization_candidates"]
        )

        # Add specific suggestions for nested loops
        nested_loop_suggestions = [
            {"line": loop["line"], "level": loop["level"], "suggestion": "Consider reducing nesting."}
            for loop in static_results["nested_loops"]
        ]

        # Generate an HTML report with all suggestions and profiling data
        formatted_static_suggestions = self.format_suggestions(static_suggestions)
        report = generate_html_report(
            formatted_static_suggestions, 
            nested_loop_suggestions, 
            runtime_profile + "\n" + memory_profile
        )

        # Save the HTML report to the project directory
        with open("report.html", "w") as report_file:
            report_file.write(report)

        print("Optimization complete. Report saved as 'report.html'.")


if __name__ == "__main__":
    import argparse

    # Parse command-line arguments to specify the script to analyze
    parser = argparse.ArgumentParser(description="Python Code Optimizer")
    parser.add_argument("script", help="Path to the Python script to analyze.")
    args = parser.parse_args()

    # Create an instance of the optimizer and run the optimization process
    optimizer = PythonOptimizer(args.script)
    optimizer.optimize()
