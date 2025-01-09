import ast

class StaticAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.nested_loops = []  # Store line numbers of nested loops
        self.high_iterations = []
        self.repeated_computations = []
        self.vectorization_candidates = []

    def visit_For(self, node):
        # Detect nested loops
        if hasattr(node, "parent") and isinstance(node.parent, ast.For):
            self.nested_loops.append(node.lineno)  # Track line number of nested loop

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
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                setattr(child, "parent", node)  # Assign parent nodes
        self.visit(tree)
        return {
            "nested_loops": self.nested_loops,
            "high_iterations": self.high_iterations,
            "repeated_computations": self.repeated_computations,
            "vectorization_candidates": self.vectorization_candidates,
        }
