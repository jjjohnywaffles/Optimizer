import ast
import astor

class RefactoringEngine(ast.NodeTransformer):
    def visit_For(self, node):
        """
        Refactor loops: Add caching for repeated computations and optimize nested loops.
        """
        # Example: Add caching for repeated computations in loops
        if isinstance(node.body, list):
            for i, stmt in enumerate(node.body):
                if isinstance(stmt, ast.Assign):
                    # Detect repeated computations in assignments
                    if isinstance(stmt.value, ast.BinOp):
                        var_name = stmt.targets[0].id  # Variable being assigned
                        computation = ast.dump(stmt.value)  # Capture the computation
                        cache_name = f"cached_{var_name}"

                        # Insert a caching check before the computation
                        cache_check = ast.If(
                            test=ast.Compare(
                                left=ast.Name(id=var_name, ctx=ast.Load()),
                                ops=[ast.NotIn()],
                                comparators=[ast.Name(id="cache", ctx=ast.Load())],
                            ),
                            body=[
                                ast.Assign(
                                    targets=[ast.Subscript(
                                        value=ast.Name(id="cache", ctx=ast.Load()),
                                        slice=ast.Name(id=var_name, ctx=ast.Load()),
                                        ctx=ast.Store(),
                                    )],
                                    value=stmt.value,
                                )
                            ],
                            orelse=[],
                        )

                        # Replace the original computation with cached value
                        stmt.value = ast.Subscript(
                            value=ast.Name(id="cache", ctx=ast.Load()),
                            slice=ast.Name(id=var_name, ctx=ast.Load()),
                            ctx=ast.Load(),
                        )

                        # Insert the caching logic before the loop body
                        node.body.insert(i, cache_check)

        # Process nested loops
        if hasattr(node, "parent") and isinstance(node.parent, ast.For):
            print(f"Refactoring nested loop at Line {node.lineno}")

        # Continue visiting children
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        """
        Add initialization for caching if required.
        """
        cache_init = ast.Assign(
            targets=[ast.Name(id="cache", ctx=ast.Store())],
            value=ast.Dict(keys=[], values=[]),
        )
        node.body.insert(0, cache_init)
        self.generic_visit(node)
        return node
