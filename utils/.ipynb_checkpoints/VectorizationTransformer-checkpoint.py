import ast
import logging

class VectorizationTransformer(ast.NodeTransformer):
    """
    Transformer to optimize Python code by vectorizing loops using NumPy.
    """
    def __init__(self):
        super().__init__()
        self.numpy_import_injected = False

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """
        Traverse the module node, assign parents to child nodes, and ensure necessary imports
        (e.g., NumPy, itertools) are added if transformations require them.
        """
        self.numpy_import_injected = False
        self.itertools_import_injected = False

        # Check existing imports
        for stmt in node.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    if alias.name == "numpy":
                        self.numpy_import_injected = True
                    elif alias.name == "itertools":
                        self.itertools_import_injected = True
            elif isinstance(stmt, ast.ImportFrom):
                if stmt.module == "numpy":
                    self.numpy_import_injected = True
                elif stmt.module == "itertools":
                    self.itertools_import_injected = True

        # Assign parents and traverse child nodes
        for child in ast.iter_child_nodes(node):
            setattr(child, "parent", node)
            self._assign_parents(child)

        # Visit function definitions or other statements
        new_body = [self.visit(stmt) if isinstance(stmt, (ast.FunctionDef, ast.ClassDef)) else stmt for stmt in node.body]

        # Add necessary imports
        if not self.numpy_import_injected:
            numpy_import = ast.Import(names=[ast.alias(name="numpy", asname="np")])
            new_body.insert(0, numpy_import)
            self.numpy_import_injected = True

        if not self.itertools_import_injected:
            itertools_import = ast.Import(names=[ast.alias(name="itertools", asname=None)])
            new_body.insert(0, itertools_import)
            self.itertools_import_injected = True

        node.body = new_body
        return node


    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """
        Traverse and apply transformations to the body of a function definition.
        """
        node.body = [self.visit(stmt) for stmt in node.body]
        return node

    def _assign_parents(self, parent_node: ast.AST):
        """
        Assign parent references to all child nodes in the AST for upward traversal.
        """
        for child in ast.iter_child_nodes(parent_node):
            setattr(child, "parent", parent_node)
            self._assign_parents(child)

    def visit_For(self, node: ast.For):
        """
        Detect and transform simple numeric loops of the form:
        for i in range(len(arr)):
            arr[i] = arr[i] + c
        into a NumPy vectorized operation.
        """
        node = self.generic_visit(node)
        if not self.is_simple_loop(node):
            return node

        if len(node.body) != 1:
            return node

        stmt = node.body[0]
        if not isinstance(stmt, (ast.Assign, ast.AugAssign)):
            return node

        target = stmt.targets[0] if isinstance(stmt, ast.Assign) else stmt.target
        value = stmt.value

        if not (isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name)):
            return node

        arr_name = target.value.id
        loop_arr_name = self.get_loop_array(node.iter)
        if arr_name != loop_arr_name:
            return node

        loop_var = node.target
        if not (isinstance(target.slice, ast.Name) and target.slice.id == loop_var.id):
            return node

        transform_type, const_expr = self.parse_expression(value, arr_name, loop_var.id)
        if not transform_type:
            return node

        logging.info("[vectorization] Detected a simple loop to vectorize on %s", arr_name)

        new_body = []
        if not self.numpy_import_injected:
            new_body.append(ast.Import(names=[ast.alias(name="numpy", asname="np")]))
            self.numpy_import_injected = True

        np_array_call = ast.Call(
            func=ast.Attribute(value=ast.Name(id="np", ctx=ast.Load()), attr="array", ctx=ast.Load()),
            args=[ast.Name(id=arr_name, ctx=ast.Load())],
            keywords=[]
        )
        assign_to_arr = ast.Assign(
            targets=[ast.Name(id=arr_name, ctx=ast.Store())],
            value=np_array_call
        )
        new_body.append(assign_to_arr)

        op_node = None
        if transform_type == "add":
            op_node = ast.BinOp(left=ast.Name(id=arr_name, ctx=ast.Load()), op=ast.Add(), right=const_expr)
        elif transform_type == "sub":
            op_node = ast.BinOp(left=ast.Name(id=arr_name, ctx=ast.Load()), op=ast.Sub(), right=const_expr)
        elif transform_type == "mult":
            op_node = ast.BinOp(left=ast.Name(id=arr_name, ctx=ast.Load()), op=ast.Mult(), right=const_expr)

        if op_node:
            vector_assign = ast.Assign(targets=[ast.Name(id=arr_name, ctx=ast.Store())], value=op_node)
            new_body.append(vector_assign)

        return ast.copy_location(ast.Module(body=new_body, type_ignores=[]), node)

    def is_simple_loop(self, node: ast.For) -> bool:
        """
        Check if the loop is of the form:
        for i in range(len(arr)):
        """
        if not (isinstance(node.target, ast.Name) and isinstance(node.iter, ast.Call)):
            return False
        call = node.iter
        if not (hasattr(call.func, "id") and call.func.id == "range"):
            return False
        if len(call.args) != 1:
            return False
        arg = call.args[0]
        return isinstance(arg, ast.Call) and hasattr(arg.func, "id") and arg.func.id == "len"

    def get_loop_array(self, call_node: ast.Call) -> str:
        """
        Extract the array name from len(arr) in the loop range.
        """
        len_call = call_node.args[0]
        if len_call.args and isinstance(len_call.args[0], ast.Name):
            return len_call.args[0].id
        return ""

    def parse_expression(self, value_node: ast.AST, arr_name: str, loop_var: str):
        """
        Parse and identify expressions of the form:
        arr[i] + c, arr[i] - c, arr[i] * c.
        """
        if not isinstance(value_node, ast.BinOp):
            return None, None

        left = value_node.left
        right = value_node.right
        op = value_node.op

        if not (isinstance(left, ast.Subscript) and isinstance(left.value, ast.Name) and left.value.id == arr_name and isinstance(left.slice, ast.Name) and left.slice.id == loop_var):
            return None, None

        if not isinstance(right, ast.Constant):
            return None, None

        if isinstance(op, ast.Add):
            return "add", right
        elif isinstance(op, ast.Sub):
            return "sub", right
        elif isinstance(op, ast.Mult):
            return "mult", right

        return None, None

