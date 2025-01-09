import ast

class RefactoringEngine(ast.NodeTransformer):
    """
    A forceful approach that, upon detecting exactly one nested loop,
    completely replaces the entire outer 'for' node with a flattened loop
    using itertools.product. This removes the old for lines entirely.
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
        1. Detect if outer_loop contains exactly one inner For node.
        2. If so, replace both with a single For node using itertools.product.
        3. Return the new flattened loop node, removing old lines.
        """
        # First, let’s visit children so we have the final structure
        self.generic_visit(outer_loop)

        # Attempt flatten
        flattened = self.flatten_nested_loop(outer_loop)
        return flattened

    def flatten_nested_loop(self, outer_loop):
        """
        If the outer_loop has exactly one inner_loop,
        create a single loop with itertools.product.
        Remove original for statements entirely.
        """
        # Find all For nodes in outer_loop.body
        inner_loops = [stmt for stmt in outer_loop.body if isinstance(stmt, ast.For)]

        # Only flatten if exactly one inner loop is present
        if len(inner_loops) != 1:
            return outer_loop  # can't flatten multiple or zero

        inner_loop = inner_loops[0]
        # Both outer_loop and inner_loop must have simple Name targets
        if (
            isinstance(outer_loop.target, ast.Name)
            and isinstance(inner_loop.target, ast.Name)
            and isinstance(outer_loop.iter, ast.Call)  # e.g. range(...)
            and isinstance(inner_loop.iter, ast.Call)  # e.g. range(...)
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

            # We unify the entire outer loop body but replace the *inner loop* 
            # with its body. Everything else in outer_loop.body remains in the new loop.

            new_body = []
            for stmt in outer_loop.body:
                if stmt is inner_loop:
                    # Replace the inner loop line with the inner loop’s body
                    new_body.extend(inner_loop.body)
                else:
                    # Keep everything else in the flattened loop
                    new_body.append(stmt)

            # Return the single flattened For node
            flattened_loop = ast.For(
                target=flattened_target,
                iter=flattened_iter,
                body=new_body,
                orelse=[],
                lineno=outer_loop.lineno,
                col_offset=outer_loop.col_offset
            )
            return flattened_loop

        return outer_loop

    def ensure_itertools_import(self, node):
        """
        Insert 'import itertools' at the module level if not already present.
        """
        # Climb the parent chain to find the Module
        current = node
        while current and not isinstance(current, ast.Module):
            current = getattr(current, "parent", None)

        if not current or not isinstance(current, ast.Module):
            return  # can't insert if we don't find a Module

        # Check if we already have 'import itertools'
        for stmt in current.body:
            if isinstance(stmt, ast.Import):
                if any(alias.name == "itertools" for alias in stmt.names):
                    return  # found it, no need to insert

        # Not found, so insert it at the top of the module
        import_itertools = ast.Import(names=[ast.alias(name="itertools", asname=None)])
        current.body.insert(0, import_itertools)