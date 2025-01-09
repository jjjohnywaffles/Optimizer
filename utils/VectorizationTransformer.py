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
        super().__init__()
        self.numpy_import_injected = False
    def visit_Module(self, node: ast.Module) -> ast.Module:
        """
        1) Assign .parent to children.
        2) Check if there's already an 'import numpy' or 'import numpy as np'.
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
    def _assign_parents(self, parent_node: ast.AST):
        for child in ast.iter_child_nodes(parent_node):
            setattr(child, "parent", parent_node)
            self._assign_parents(child)
    def visit_For(self, node: ast.For):
        """
        Look for:
          for i in range(len(arr)):
              arr[i] OP= <const_expr>
        If found, rewrite to a NumPy vector operation.
        """
        node = self.generic_visit(node)  # Visit children first
        # Check if it's for i in range(len(...)):
        if not self.is_simple_loop(node):
            return node
        # Now see if body has 1 statement that modifies arr[i].
        if len(node.body) != 1:
            return node
        stmt = node.body[0]
        if not isinstance(stmt, ast.Assign) and not isinstance(stmt, ast.AugAssign):
            return node
        # Distinguish between x = <expr> vs x += <expr>
        if isinstance(stmt, ast.Assign):
            target = stmt.targets[0]
            value = stmt.value
        else:  # AugAssign
            target = stmt.target
            value = stmt.value
        # Check that target is arr[i] for the same arr as in range(len(arr))
        if not (isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name)):
            return node
        arr_name = target.value.id
        loop_arr_name = self.get_loop_array(node.iter)
        if arr_name != loop_arr_name:
            return node
        # Check if the index is the loop var (like for i in range(len(arr)): arr[i] = ...)
        loop_var = node.target
        if not (isinstance(target.slice, ast.Name) and target.slice.id == loop_var.id):
            return node
        # Now see if it's a simple operation with a constant or numeric expression
        # e.g. arr[i] = arr[i] + c
        # We check if arr[i] is on left side of the expression or in an AugAssign
        # For simplicity, let's handle "arr[i] = arr[i] + <something>" or "arr[i] += <something>"
        transform_type, const_expr = self.parse_expression(value, arr_name, loop_var.id)
        if not transform_type:
            return node
        # If we got here, we have a recognized pattern! Let's vectorize it
        logging.info("[vectorization] Detected a simple loop to vectorize on %s", arr_name)
        # We'll build a small block of statements:
        #  1) Import numpy as np (if not present)
        #  2) arr = np.array(arr)
        #  3) arr = arr <op> <const_expr>
        new_body = []
        if not self.numpy_import_injected:
            # Insert: import numpy as np
            import_numpy = ast.Import(names=[ast.alias(name="numpy", asname="np")])
            new_body.append(import_numpy)
            self.numpy_import_injected = True
        #  arr = np.array(arr)
        # We'll do: arr = np.array(ast.Name(arr_name))
        arr_var = ast.Name(id=arr_name, ctx=ast.Load())
        np_array_call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="np", ctx=ast.Load()),
                attr="array",
                ctx=ast.Load()
            ),
            args=[arr_var],
            keywords=[]
        )
        assign_to_arr = ast.Assign(
            targets=[ast.Name(id=arr_name, ctx=ast.Store())],
            value=np_array_call
        )
        new_body.append(assign_to_arr)
        #  arr = arr +/- const_expr
        op_node = None
        if transform_type == "add":
            # arr = arr + const_expr
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
        elif transform_type == "mult":
            op_node = ast.BinOp(
                left=ast.Name(id=arr_name, ctx=ast.Load()),
                op=ast.Mult(),
                right=const_expr
            )
        # Extend for div, etc.
        if op_node:
            vector_assign = ast.Assign(
                targets=[ast.Name(id=arr_name, ctx=ast.Store())],
                value=op_node
            )
            new_body.append(vector_assign)
        # Return the new body as a replacement for this entire for-loop
        block = ast.copy_location(ast.Module(body=new_body, type_ignores=[]), node)
        return block
    def is_simple_loop(self, node: ast.For) -> bool:
        """
        Check pattern: for i in range(len(x)):
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
        Returns the array name used in len(...).
        e.g. for i in range(len(arr)): -> returns "arr"
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
        Distinguish expressions like:
          arr[i] + c
          arr[i] - c
          arr[i] * c
        Or arr[i] + arr[i], etc. 
        For simplicity, let's handle arr[i] + <Constant>.
        Returns (transform_type, const_expr_node) or (None, None).
        transform_type in {"add", "sub", "mult"} ...
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