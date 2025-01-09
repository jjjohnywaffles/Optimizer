import ast
import logging

class VectorizationTransformer(ast.NodeTransformer):
    """
    Detect loops of the form:
      for i in range(len(arr)):
          arr[i] = arr[i] + c
    Then rewrite to:
      import numpy as np
      arr = np.array(arr)
      arr = arr + c
    """

    def __init__(self):
        """
        Initialize the transformer.
        Tracks whether 'import numpy' or 'import numpy as np' is already present
        in the script to avoid redundant imports.
        """
        super().__init__()
        self.numpy_import_injected = False

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """
        Process the module-level AST node.
        - Assign .parent to each child for easier traversal and context tracking.
        - Check if the script already imports NumPy.
        - Optionally inject a NumPy import if vectorization occurs.

        Args:
            node (ast.Module): The module node representing the entire script.

        Returns:
            ast.Module: The transformed module node.
        """
        # Mark if we already import numpy
        for stmt in node.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    if alias.name == "numpy":
                        self.numpy_import_injected = True
            elif isinstance(stmt, ast.ImportFrom):
                if stmt.module == "numpy":
                    self.numpy_import_injected = True

        # Recursively set parents and visit
        for child in ast.iter_child_nodes(node):
            setattr(child, "parent", node)
            self._assign_parents(child)
        node = self.generic_visit(node)

        # If we performed a vectorization but never saw a numpy import, insert one at the top
        # We'll only know if we actually need it after we detect a transform, so we can do that in For or after. 
        # But let's handle it here for demonstration:
        if not self.numpy_import_injected:
            # We'll conditionally inject if we do any vectorization in 'visit_For'
            pass

        return node
    
    def build_vectorized_code(self, arr_name: str, transform_type: str, const_expr: ast.Constant):
        """
        Construct vectorized NumPy code for the loop.
        """
        new_body = []

        # Import numpy if needed
        if not self.numpy_import_injected:
            import_numpy = ast.Import(names=[ast.alias(name="numpy", asname="np")])
            new_body.append(import_numpy)
            self.numpy_import_injected = True

        # Convert arr to np.array
        arr_var = ast.Name(id=arr_name, ctx=ast.Load())
        np_array_call = ast.Call(
            func=ast.Attribute(value=ast.Name(id="np", ctx=ast.Load()), attr="array", ctx=ast.Load()),
            args=[arr_var],
            keywords=[]
        )
        assign_to_arr = ast.Assign(targets=[ast.Name(id=arr_name, ctx=ast.Store())], value=np_array_call)
        new_body.append(assign_to_arr)

        # Apply the vectorized operation
        if transform_type == "add":
            op_node = ast.BinOp(
                left=ast.Name(id=arr_name, ctx=ast.Load()),
                op=ast.Add(),
                right=const_expr
            )
        elif transform_type == "sub":
            op_node = ast.BinOp(
                left=ast.Name(id=arr_name, ctx=ast.Load()),
                op=ast.Sub(),
                right=const_expr
            )
        # Extend for other operations as needed.

        vector_assign = ast.Assign(targets=[ast.Name(id=arr_name, ctx=ast.Store())], value=op_node)
        new_body.append(vector_assign)

        return new_body
    
    def ensure_numpy_import(self, node: ast.Module):
        """
        Ensure that 'import numpy as np' is present in the module.
        """
        for stmt in node.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    if alias.name == "numpy":
                        return
            if isinstance(stmt, ast.ImportFrom) and stmt.module == "numpy":
                return

        import_numpy = ast.Import(names=[ast.alias(name="numpy", asname="np")])
        node.body.insert(0, import_numpy)

    
    def _assign_parents(self, parent_node: ast.AST):
        """
        Recursively assign the .parent attribute to all child nodes.
        This allows traversal back up the AST hierarchy when necessary.

        Args:
            parent_node (ast.AST): The current parent node.
        """
        for child in ast.iter_child_nodes(parent_node):
            setattr(child, "parent", parent_node)
            self._assign_parents(child)

    def visit_For(self, node: ast.For):
        """
        Detect and refactor loops for potential optimizations:
        1. Vectorize simple numeric loops (e.g., arr[i] = arr[i] + c).
        2. Flatten nested loops if applicable.
        """
        # Visit child nodes first
        node = self.generic_visit(node)

        # Check if the loop is eligible for vectorization
        if self.is_simple_loop(node):
            arr_name = self.get_loop_array(node.iter)
            loop_var = node.target

            # Ensure it's a simple operation within the loop
            if len(node.body) == 1:
                stmt = node.body[0]
                if isinstance(stmt, (ast.Assign, ast.AugAssign)):
                    target = stmt.targets[0] if isinstance(stmt, ast.Assign) else stmt.target
                    value = stmt.value

                    # Ensure target matches the array and loop variable
                    if (
                        isinstance(target, ast.Subscript)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == arr_name
                        and isinstance(target.slice, ast.Name)
                        and target.slice.id == loop_var.id
                    ):
                        transform_type, const_expr = self.parse_expression(value, arr_name, loop_var.id)
                        if transform_type:
                            logging.info(f"[vectorization] Vectorizing loop for {arr_name} with operation {transform_type}")

                            # Ensure NumPy import is present
                            mod_node = self.find_module_node(node)
                            if mod_node:
                                self.ensure_numpy_import(mod_node)

                            # Build the vectorized code
                            new_body = self.build_vectorized_code(arr_name, transform_type, const_expr)

                            # Return a new AST node replacing the loop
                            return ast.copy_location(ast.Module(body=new_body, type_ignores=[]), node)

        # If vectorization is not possible, attempt to flatten nested loops
        return self.flatten_nested_loop(node)


    def is_simple_loop(self, node: ast.For) -> bool:
        """
        Check if the loop matches the pattern:
          for i in range(len(arr)):
        Ensures the loop iterates over a range determined by the length of an array.

        Args:
            node (ast.For): The `for` loop node.

        Returns:
            bool: True if the loop matches the pattern; otherwise, False.
        """
        # for i in ...
        if not (isinstance(node.target, ast.Name) and isinstance(node.iter, ast.Call)):
            return False
        call = node.iter
        if not (hasattr(call.func, "id") and call.func.id == "range"):
            return False
        # range(len(...))
        if len(call.args) != 1:
            return False
        arg = call.args[0]
        if not (isinstance(arg, ast.Call) and hasattr(arg.func, "id") and arg.func.id == "len"):
            return False
        # len(...)
        return True

    def get_loop_array(self, call_node: ast.Call) -> str:
        """
        Extract the array name from the `len()` function in the loop.
        e.g., for i in range(len(arr)): -> returns "arr".

        Args:
            call_node (ast.Call): The `range(len(...))` call node.

        Returns:
            str: The name of the array being iterated over.
        """
        # call_node = range(len(...))
        # call_node.args[0] = Call(func=Name(id='len',...))
        len_call = call_node.args[0]
        if not len_call.args:
            return ""
        if isinstance(len_call.args[0], ast.Name):
            return len_call.args[0].id
        return ""

    def parse_expression(self, value_node: ast.AST, arr_name: str, loop_var: str):
        """
        Parse the right-hand side of an assignment or augmented assignment.
        Detect and classify operations such as:
          arr[i] + c, arr[i] - c, arr[i] * c, etc.

        Args:
            value_node (ast.AST): The expression node.
            arr_name (str): The name of the array being modified.
            loop_var (str): The loop variable.

        Returns:
            tuple: A tuple containing the type of transformation ("add", "sub", "mult") 
                   and the constant or expression node.
        """
        # We want something like:
        # BinOp(left=Subscript(value=Name(arr_name), slice=Name(loop_var)), op=Add(), right=Constant)
        if not isinstance(value_node, ast.BinOp):
            # Could be a single name/constant if in an AugAssign scenario
            return (None, None)
        left = value_node.left
        right = value_node.right
        op = value_node.op

        # Check left side is arr[i]
        if not (isinstance(left, ast.Subscript) and
                isinstance(left.value, ast.Name) and left.value.id == arr_name and
                isinstance(left.slice, ast.Name) and left.slice.id == loop_var):
            return (None, None)

        # Check right side is a constant or numeric expression (we’ll accept a constant for now)
        if not isinstance(right, ast.Constant):
            return (None, None)

        if isinstance(op, ast.Add):
            return ("add", right)
        elif isinstance(op, ast.Sub):
            return ("sub", right)
        elif isinstance(op, ast.Mult):
            return ("mult", right)

        return (None, None)
