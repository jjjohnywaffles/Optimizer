import ast

class StaticAnalyzer(ast.NodeVisitor):
    
    """
    A static analyzer for Python code that identifies potential optimization opportunities:
      - Detects nested loops and tracks their levels of nesting.
      - Flags loops with high iteration counts.
      - Identifies repeated computations within loops that could benefit from caching.
      - Prepares data for potential vectorization of loops.
    """
    
    def __init__(self):
        
        """
        Initialize the static analyzer with empty lists to store detected patterns:
          - nested_loops: Stores information about nested loops, including line number and nesting level.
          - high_iterations: Tracks loops with iteration counts exceeding a threshold (e.g., > 1000).
          - repeated_computations: Detects and records repeated operations in loop bodies.
          - vectorization_candidates: Placeholder for future implementation of vectorization suggestions.
        """
        
        self.nested_loops = []  # Store dicts with line numbers and levels of nesting
        self.high_iterations = []
        self.repeated_computations = []
        self.vectorization_candidates = []

    def visit_For(self, node):
        
        """
        Visit a 'for' loop node to analyze its structure and detect optimization opportunities:
          - Detect nested loops: Traverse up the AST to count nesting levels and record them.
          - Detect high-iteration loops: Identify loops with a large number of iterations by analyzing `range` calls.

        Args:
            node (ast.For): The AST node representing a 'for' loop.
        """
        # Detect and track nested loops with nesting levels
        nesting_level = 0
        current = node
        while hasattr(current, "parent"):
            if isinstance(current.parent, ast.For):
                nesting_level += 1
            current = current.parent

        if nesting_level > 0:
            self.nested_loops.append({"line": node.lineno, "level": nesting_level})

        # Detect loops with high iterations
        if isinstance(node.iter, ast.Call) and getattr(node.iter.func, "id", None) == "range":
            if node.iter.args:
                arg = node.iter.args[0]
                if isinstance(arg, ast.Constant) and arg.value > 1000:
                    self.high_iterations.append(
                        f"Line {node.lineno}: Consider optimizing loop with range({arg.value})."
                    )

        self.generic_visit(node)


    def visit_BinOp(self, node):
        
        """
        Visit a binary operation (e.g., addition, multiplication) to detect repeated computations in loops.

        Repeated computations are identified by traversing up the AST to check if the operation
        is within a loop. If so, they are flagged for potential caching.

        Args:
            node (ast.BinOp): The AST node representing a binary operation.
        """
        
        if isinstance(node.op, (ast.Add, ast.Mult)):
            # Traverse up the parent chain to check if the node belongs to a loop
            current = node
            while hasattr(current, "parent"):
                current = current.parent
                if isinstance(current, ast.For):
                    self.repeated_computations.append(
                        f"Line {node.lineno}: Consider caching repeated computation '{ast.dump(node)}'."
                    )
                    break
        self.generic_visit(node)
        
    def analyze(self, source_code):
        """
        Perform static analysis on the provided source code to identify optimization opportunities.

        The analysis involves:
          - Parsing the source code into an AST.
          - Assigning parent nodes for traversal and context-sensitive analysis.
          - Visiting nodes to collect information about nested loops, high iterations, and repeated computations.

        Args:
            source_code (str): The Python source code to analyze.

        Returns:
            dict: A dictionary containing:
              - 'nested_loops': List of detected nested loops with line numbers and nesting levels.
              - 'high_iterations': List of loops with high iteration counts.
              - 'repeated_computations': List of repeated computations detected in loops.
              - 'vectorization_candidates': Placeholder list for potential vectorization opportunities.
        """
        
        # Parse the source code into an AST
        tree = ast.parse(source_code)

        # Assign parent nodes for context-sensitive traversal
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                setattr(child, "parent", node)  # Assign parent nodes

        # Visit all nodes in the AST
        self.visit(tree)

        # Return the analysis results
        return {
            "nested_loops": self.nested_loops,
            "high_iterations": self.high_iterations,
            "repeated_computations": self.repeated_computations,
            "vectorization_candidates": self.vectorization_candidates,
        }
