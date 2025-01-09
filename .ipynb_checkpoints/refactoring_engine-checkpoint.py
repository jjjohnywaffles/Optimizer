import ast
import astor

class RefactoringEngine(ast.NodeTransformer):
    def visit_For(self, node):
        # Replace simple loops with NumPy vectorization
        if isinstance(node.target, ast.Name) and isinstance(node.iter, ast.Call):
            if getattr(node.iter.func, "id", None) == "range":
                print(f"Vectorizing loop at Line {node.lineno}")
                return ast.parse("arr += 1").body[0]
        return node
