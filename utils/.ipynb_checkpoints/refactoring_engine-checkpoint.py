import ast


class RefactoringEngine(ast.NodeTransformer):
    """
    RefactoringEngine that:
      - Flattens nested loops using itertools.product.
      - Vectorizes simple numeric loops using NumPy.
    """

    def visit_Module(self, node):
        """
        Assign .parent to each child so we can climb the AST as needed.
        """
        for child in ast.iter_child_nodes(node):
            setattr(child, "parent", node)
            self._set_parents(child)
        self.generic_visit(node)
        return node

    def _set_parents(self, parent_node):
        for child in ast.iter_child_nodes(parent_node):
            setattr(child, "parent", parent_node)
            self._set_parents(child)

    def visit_For(self, outer_loop):
        """
        1. Detect if outer_loop contains exactly one inner For node and flatten.
        2. Detect if the loop can be vectorized using NumPy.
        3. Return the modified loop.
        """
        # First, visit children so we have the final structure
        self.generic_visit(outer_loop)

        # Attempt to flatten nested loops
        flattened = self.flatten_nested_loop(outer_loop)
        if flattened is not outer_loop:
            return flattened

        # Attempt NumPy vectorization
        vectorized = self.vectorize_numeric_loop(outer_loop)
        return vectorized

    def flatten_nested_loop(self, outer_loop):
        """
        Flatten a nested loop into a single loop using itertools.product.
        """
        # Find all For nodes in outer_loop.body
        inner_loops = [stmt for stmt in outer_loop.body if isinstance(stmt, ast.For)]

        # Only flatten if exactly one inner loop is present
        if len(inner_loops) != 1:
            return outer_loop

        inner_loop = inner_loops[0]
        # Both outer_loop and inner_loop must have simple Name targets
        if (
            isinstance(outer_loop.target, ast.Name)
            and isinstance(inner_loop.target, ast.Name)
            and isinstance(outer_loop.iter, ast.Call)
            and isinstance(inner_loop.iter, ast.Call)
        ):
            # Insert 'import itertools' at the top if needed
            self.ensure_itertools_import(outer_loop)

            # Build a new single For node
            flattened_target = ast.Tuple(
                elts=[outer_loop.target, inner_loop.target],
                ctx=ast.Store()
            )

            flattened_iter = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="itertools", ctx=ast.Load()),
                    attr="product",
                    ctx=ast.Load()
                ),
                args=[outer_loop.iter, inner_loop.iter],
                keywords=[]
            )

            # Replace inner loop with its body in the flattened loop
            new_body = []
            for stmt in outer_loop.body:
                if stmt is inner_loop:
                    new_body.extend(inner_loop.body)
                else:
                    new_body.append(stmt)

            return ast.For(
                target=flattened_target,
                iter=flattened_iter,
                body=new_body,
                orelse=[],
                lineno=outer_loop.lineno,
                col_offset=outer_loop.col_offset
            )
        return outer_loop

    def ensure_itertools_import(self, node):
        """
        Insert 'import itertools' at the module level if not already present.
        """
        module = self.find_module_node(node)
        if not module:
            return

        # Check if 'itertools' is already imported
        for stmt in module.body:
            if isinstance(stmt, ast.Import):
                if any(alias.name == "itertools" for alias in stmt.names):
                    return

        # Not found, insert import statement
        module.body.insert(
            0,
            ast.Import(names=[ast.alias(name="itertools", asname=None)])
        )

    def vectorize_numeric_loop(self, loop_node):
        """
        Detect and replace simple numeric loops with NumPy operations.
        """
        # Quick check: for i in range(len(arr)):
        if not (isinstance(loop_node.iter, ast.Call)
                and isinstance(loop_node.iter.func, ast.Name)
                and loop_node.iter.func.id == "range"):
            return loop_node

        # Check if body is a single assignment: arr[i] = arr[i] <op> <value>
        if len(loop_node.body) == 1 and isinstance(loop_node.body[0], ast.Assign):
            stmt = loop_node.body[0]
            if len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Subscript):
                target = stmt.targets[0]
                if isinstance(target.value, ast.Name):
                    array_name = target.value.id
                    return self.build_vectorized_block(loop_node, array_name, stmt.value)

        return loop_node

    def build_vectorized_block(self, loop_node, array_name, value_node):
        """
        Convert a loop to a NumPy operation:
        - Add `import numpy as np` if not already present.
        - Replace the loop with a NumPy-based transformation.
        """
        # Ensure 'import numpy as np' exists
        module = self.find_module_node(loop_node)
        if module:
            self.ensure_numpy_import(module)

        # Create NumPy transformation: arr = arr + <value>
        vectorized_assign = ast.Assign(
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
                op=ast.Add(),
                right=value_node
            )
        )

        # Return the new block
        return ast.copy_location(vectorized_assign, loop_node)

    def ensure_numpy_import(self, module_node):
        """
        Add `import numpy as np` to the module if not already present.
        """
        for stmt in module_node.body:
            if isinstance(stmt, ast.Import):
                if any(alias.name == "numpy" for alias in stmt.names):
                    return

        # Add import if not found
        module_node.body.insert(
            0,
            ast.Import(names=[ast.alias(name="numpy", asname="np")])
        )

    def find_module_node(self, node):
        """
        Traverse the parent chain to find the root module node.
        """
        current = node
        while current and not isinstance(current, ast.Module):
            current = getattr(current, "parent", None)
        return current
