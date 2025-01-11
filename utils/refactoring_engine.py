import ast
import itertools

class RefactoringEngine(ast.NodeTransformer):
    """
    RefactoringEngine to optimize Python code by:
      - Flattening nested loops using itertools.product.
      - Vectorizing simple numeric loops using NumPy.
      - Converting loops into list comprehensions.
      - Unrolling small loops for performance gains.
    """

    def __init__(self):
        self.transformed_nodes = set()

    def visit_For(self, node):
        if node in self.transformed_nodes:
            return node

        self.generic_visit(node)

        # Apply transformations sequentially
        node = self.flatten_nested_loop(node)
        node = self.vectorize_numeric_loop(node)
        node = self.convert_to_list_comprehension(node)
        node = self.unroll_small_loops(node)

        self.transformed_nodes.add(node)
        return node

    def flatten_nested_loop(self, node):
        """
        Flatten nested loops using `itertools.product`, ensuring proper scoping.
        """
        if len(node.body) != 1 or not isinstance(node.body[0], ast.For):
            return node

        inner_loop = node.body[0]
        if (
            isinstance(node.target, ast.Name)
            and isinstance(inner_loop.target, ast.Name)
            and isinstance(node.iter, ast.Call)
            and isinstance(inner_loop.iter, ast.Call)
            and isinstance(inner_loop.iter.args[0], ast.Call)
            and isinstance(inner_loop.iter.args[0].func, ast.Name)
            and inner_loop.iter.args[0].func.id == "len"
        ):
            outer_var = node.target.id
            inner_var = inner_loop.target.id

            if outer_var == inner_var:
                outer_var = f"{outer_var}_outer"
                inner_var = f"{inner_var}_inner"

            # Extract matrix name dynamically
            if isinstance(inner_loop.iter.args[0].args[0], ast.Name):
                matrix_name = inner_loop.iter.args[0].args[0].id
            else:
                return node  # If the matrix name cannot be resolved, skip transformation

            # Create iterables for itertools.product
            outer_range = node.iter
            inner_range = ast.Call(
                func=ast.Name(id="len", ctx=ast.Load()),
                args=[
                    ast.Subscript(
                        value=ast.Name(id=matrix_name, ctx=ast.Load()),
                        slice=ast.Index(value=ast.Constant(value=0)),
                        ctx=ast.Load(),
                    )
                ],
                keywords=[],
            )

            flattened_target = ast.Tuple(
                elts=[
                    ast.Name(id=outer_var, ctx=ast.Store()),
                    ast.Name(id=inner_var, ctx=ast.Store()),
                ],
                ctx=ast.Store(),
            )

            flattened_iter = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="itertools", ctx=ast.Load()),
                    attr="product",
                    ctx=ast.Load(),
                ),
                args=[outer_range, inner_range],
                keywords=[],
            )

            new_body = inner_loop.body
            return ast.For(
                target=flattened_target,
                iter=flattened_iter,
                body=new_body,
                orelse=[],
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        return node


    def vectorize_numeric_loop(self, node):
        if (
            isinstance(node.iter, ast.Call) and
            isinstance(node.iter.func, ast.Name) and
            node.iter.func.id == "range" and
            len(node.body) == 1 and
            isinstance(node.body[0], (ast.AugAssign, ast.Assign))
        ):
            stmt = node.body[0]
            if isinstance(stmt, ast.Assign):
                target = stmt.targets[0]
                value = stmt.value
            else:  # AugAssign
                target = stmt.target
                value = stmt.value

            if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                array_name = target.value.id
                self.ensure_numpy_import(node)

                # Convert to vectorized operation
                return ast.Assign(
                    targets=[ast.Name(id=array_name, ctx=ast.Store())],
                    value=ast.BinOp(
                        left=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id="np", ctx=ast.Load()),
                                attr="array",
                                ctx=ast.Load()
                            ),
                            args=[ast.Name(id=array_name, ctx=ast.Load())],
                            keywords=[]
                        ),
                        op=stmt.op if isinstance(stmt, ast.AugAssign) else ast.Add(),
                        right=value
                    )
                )
        return node

    def convert_to_list_comprehension(self, node):
        if not isinstance(node, ast.For):
            return node

        if (
            isinstance(node.iter, ast.Call) and
            isinstance(node.iter.func, ast.Name) and
            node.iter.func.id == "range" and
            len(node.body) == 1 and
            isinstance(node.body[0], ast.Assign) and
            len(node.body[0].targets) == 1
        ):
            target = node.body[0].targets[0]
            if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                array_name = target.value.id
                comprehension = ast.ListComp(
                    elt=node.body[0].value,
                    generators=[
                        ast.comprehension(
                            target=node.target,
                            iter=node.iter,
                            ifs=[],
                            is_async=0
                        )
                    ]
                )
                return ast.Assign(
                    targets=[ast.Name(id=array_name, ctx=ast.Store())],
                    value=comprehension
                )
        return node

    def unroll_small_loops(self, node):
        if not isinstance(node, ast.For):
            return node

        if (
            isinstance(node.iter, ast.Call) and
            isinstance(node.iter.func, ast.Name) and
            node.iter.func.id == "range" and
            isinstance(node.iter.args[0], ast.Constant) and
            node.iter.args[0].value <= 5
        ):
            new_body = []
            for i in range(node.iter.args[0].value):
                for stmt in node.body:
                    copied_stmt = ast.fix_missing_locations(ast.copy_location(stmt, stmt))
                    new_body.append(copied_stmt)
            return new_body
        return node

        def replace_loop_variable(self, stmt, loop_var, replacement):
            """
            Replace occurrences of the loop variable in the given statement.
            """
            class LoopVarReplacer(ast.NodeTransformer):
                def visit_Name(self, node):
                    if node.id == loop_var.id:
                        return ast.copy_location(replacement, node)
                    return node

            return LoopVarReplacer().visit(stmt)

    def ensure_itertools_import(self, node):
        module = self.find_module_node(node)
        if not module:
            return
        for stmt in module.body:
            if isinstance(stmt, ast.Import) and any(alias.name == "itertools" for alias in stmt.names):
                return
        module.body.insert(0, ast.Import(names=[ast.alias(name="itertools", asname=None)]))

    def ensure_numpy_import(self, node):
        module = self.find_module_node(node)
        if not module:
            return
        for stmt in module.body:
            if isinstance(stmt, ast.Import) and any(alias.name == "numpy" for alias in stmt.names):
                return
        module.body.insert(0, ast.Import(names=[ast.alias(name="numpy", asname="np")]))

    def find_module_node(self, node):
        while node and not isinstance(node, ast.Module):
            node = getattr(node, "parent", None)
        return node
