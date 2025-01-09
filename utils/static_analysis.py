import ast

class StaticAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.nested_loops = []  # Store dicts with line numbers and levels of nesting
        self.high_iterations = []
        self.repeated_computations = []
        self.vectorization_candidates = []

    def visit_For(self, node):
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
