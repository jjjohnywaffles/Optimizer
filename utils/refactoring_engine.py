import ast

class RefactoringEngine(ast.NodeTransformer):
    """
    RefactoringEngine that:
      - Flattens nested loops using itertools.product.
      - Vectorizes simple numeric loops using NumPy.
    """

    def contains_numpy_usage(self, node):
        """
        Check if the AST node contains any usage of 'np.'.

        Args:
            node (ast.AST): The root node to traverse.

        Returns:
            bool: True if 'np.' usage is found, False otherwise.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name):
                if child.value.id == "np":
                    return True
        return False
    
    def visit_Module(self, node):
        """
        Visit the root module node and ensure necessary imports after processing.
        """
        # Traverse the tree to set parent nodes and apply transformations
        for child in ast.iter_child_nodes(node):
            setattr(child, "parent", node)
            self._set_parents(child)
        self.generic_visit(node)

        # Check for NumPy usage and add the import if necessary
        if self.contains_numpy_usage(node):
            self.ensure_numpy_import(node)

        return node
    
    

    def _set_parents(self, parent_node):
        """
        Recursively assign `.parent` attributes to child nodes for upward traversal.

        Args:
            parent_node (ast.AST): The current parent node to process.
        """
        for child in ast.iter_child_nodes(parent_node):
            setattr(child, "parent", parent_node)
            self._set_parents(child)

    def visit_For(self, outer_loop):
        """
        Process a `for` loop to:
          1. Flatten nested loops using `itertools.product`.
          2. Vectorize simple numeric loops using NumPy.

        Args:
            outer_loop (ast.For): The outer loop node to analyze and transform.

        Returns:
            ast.AST: The transformed loop node, or the original if no transformations apply.
        """
        # Visit children first to ensure correct tree structure
        self.generic_visit(outer_loop)

        # Attempt to flatten nested loops
        flattened = self.flatten_nested_loop(outer_loop)
        if flattened is not outer_loop:
            return flattened

        # Attempt to vectorize numeric loops
        vectorized = self.vectorize_numeric_loop(outer_loop)
        return vectorized

    def flatten_nested_loop(self, outer_loop):
        """
        Flatten a nested loop into a single loop with `itertools.product`.

        Args:
            outer_loop (ast.For): The outer loop node containing a nested loop.

        Returns:
            ast.For: A flattened loop node, or the original if no changes are made.
        """
        inner_loops = [stmt for stmt in outer_loop.body if isinstance(stmt, ast.For)]

        # Only flatten if exactly one inner loop is present
        if len(inner_loops) != 1:
            return outer_loop

        inner_loop = inner_loops[0]
        if (
            isinstance(outer_loop.target, ast.Name)
            and isinstance(inner_loop.target, ast.Name)
            and isinstance(outer_loop.iter, ast.Call)
            and isinstance(inner_loop.iter, ast.Call)
        ):
            self.ensure_itertools_import(outer_loop)

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
        Add `import itertools` to the module if it is not already present.

        Args:
            node (ast.AST): The node within the module to inspect for imports.
        """
        module = self.find_module_node(node)
        if not module:
            return

        for stmt in module.body:
            if isinstance(stmt, ast.Import):
                if any(alias.name == "itertools" for alias in stmt.names):
                    return

        module.body.insert(
            0,
            ast.Import(names=[ast.alias(name="itertools", asname=None)])
        )

    def vectorize_numeric_loop(self, loop_node):
        """
        Detect and replace simple numeric loops with equivalent NumPy operations.

        Args:
            loop_node (ast.For): The loop node to analyze for vectorization.

        Returns:
            ast.AST: A NumPy-based transformation or the original loop if no vectorization applies.
        """
        if not (isinstance(loop_node.iter, ast.Call)
                and isinstance(loop_node.iter.func, ast.Name)
                and loop_node.iter.func.id == "range"):
            return loop_node

        if len(loop_node.body) == 1 and isinstance(loop_node.body[0], ast.Assign):
            stmt = loop_node.body[0]
            if len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Subscript):
                target = stmt.targets[0]
                if isinstance(target.value, ast.Name):
                    array_name = target.value.id
                    vectorized_code = self.build_vectorized_code(array_name, stmt.value)
                    setattr(vectorized_code, "vectorized", True)  # Add marker
                    return vectorized_code

        return loop_node

    def build_vectorized_code(self, arr_name: str, value_node: ast.AST):
        """
        Convert a loop into a vectorized NumPy transformation.

        Args:
            arr_name (str): The name of the array being modified in the loop.
            value_node (ast.AST): The value or operation applied in the loop.

        Returns:
            ast.AST: A new block of code replacing the loop with a NumPy transformation.
        """
        module = self.find_module_node(value_node)
        if module:
            self.ensure_numpy_import(module)

        vectorized_assign = ast.Assign(
            targets=[ast.Name(id=arr_name, ctx=ast.Store())],
            value=ast.BinOp(
                left=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="np", ctx=ast.Load()),
                        attr="array",
                        ctx=ast.Load()
                    ),
                    args=[ast.Name(id=arr_name, ctx=ast.Load())],
                    keywords=[]
                ),
                op=ast.Add(),
                right=value_node
            )
        )

        return vectorized_assign

    def ensure_numpy_import(self, module_node):
        """
        Add `import numpy as np` to the module if it is not already present.

        Args:
            module_node (ast.Module): The module node to inspect and modify.
        """
        for stmt in module_node.body:
            if isinstance(stmt, ast.Import):
                if any(alias.name == "numpy" for alias in stmt.names):
                    return  # NumPy already imported

        # Insert NumPy import after existing imports or docstrings
        insert_idx = 0
        for idx, stmt in enumerate(module_node.body):
            if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Str)):
                insert_idx = idx
                break

        module_node.body.insert(
            insert_idx,
            ast.Import(names=[ast.alias(name="numpy", asname="np")])
        )
        print(ast.dump(module_node, indent=4))

    def find_module_node(self, node):
        """
        Traverse the parent chain to find the root module node.

        Args:
            node (ast.AST): The starting node.

        Returns:
            ast.Module: The root module node, or None if not found.
        """
        current = node
        while current and not isinstance(current, ast.Module):
            current = getattr(current, "parent", None)
        return current
