from typing import Dict, List, Any, Optional
from lexer_parser import ASTNode, TokenType
from collections import deque

class RuntimeError(Exception):
    pass

class Function:
    def __init__(self, name: str, parameters: List[ASTNode], body: List[ASTNode]):
        self.name = name
        self.parameters = parameters
        self.body = body

class Runtime:
    def __init__(self):
        # Memory management
        self.variables: Dict[str, Any] = {}
        self.constants: Dict[str, Any] = {}
        self.functions: Dict[str, Function] = {}
        
        # Data structures
        self.arrays: Dict[str, List] = {}
        self.stacks: Dict[str, List] = {}
        self.queues: Dict[str, deque] = {}
        
        # Function call management
        self.return_value = None
        self.current_scope: List[Dict[str, Any]] = []
        self.last_input = None

    def reset(self):
        self.variables.clear()
        self.constants.clear()
        self.functions.clear()
        self.arrays.clear()
        self.stacks.clear()
        self.queues.clear()
        self.return_value = None
        self.current_scope = []
        self.last_input = None

    def execute(self, ast: List[ASTNode]) -> Any:
        self.reset()
        result = None
        for node in ast:
            result = self.execute_node(node)
        return result

    def execute_node(self, node: ASTNode) -> Any:
        if node is None:
            return None
        
        handlers = {
            'declaration': self.execute_declaration,
            'constant_declaration': self.execute_constant,
            'print': self.execute_print,
            'binary_op': self.execute_binary_op,
            'integer_literal': lambda n: int(n.value),
            'string_literal': lambda n: str(n.value),
            'boolean_literal': lambda n: bool(n.value),
            'identifier': lambda n: self.get_variable(n.value),
            'if': self.execute_if,
            'while': self.execute_while,
            'for': self.execute_for,
            'method': self.execute_method_definition,
            'function_call': self.execute_function_call,
            'method_call': self.execute_method_call,
            'return': self.execute_return,
            'array_declaration': self.execute_array_declaration,
            'string_operation': self.execute_string_operation,
            'input': self.execute_input,
            'input_expression': self.execute_input_expression,
            'data_structure_declaration': self.execute_data_structure_declaration,
            'comment': lambda n: None,
            'block': self.execute_block,
            'assignment': self.execute_assignment,
            'ternary_op': self.execute_ternary_op,
            'array_access': self.execute_array_access,
            'array_assignment': self.execute_array_assignment,
        }
        
        handler = handlers.get(node.type)
        if handler:
            return handler(node)
        raise RuntimeError(f"Unknown node type: {node.type}")

    def push_scope(self):
        self.current_scope.append(self.variables.copy())
        self.variables = {}

    def pop_scope(self):
        if self.current_scope:
            self.variables = self.current_scope.pop()

    def execute_assignment(self, node: ASTNode) -> None:
        var_name = node.value['identifier']
        if var_name in self.constants:
            raise RuntimeError(f"Cannot reassign constant {var_name}")
        value = self.execute_node(node.children[0])
        
        if var_name in self.variables:
            self.variables[var_name] = value
            return
            
        for scope in reversed(self.current_scope):
            if var_name in scope:
                scope[var_name] = value
                return
                
        self.variables[var_name] = value

    def execute_constant(self, node: ASTNode) -> None:
        const_name = node.value['name']
        value = self.execute_node(node.children[0])
        if const_name in self.constants:
            raise RuntimeError(f"Cannot redefine constant {const_name}")
        self.constants[const_name] = value

    def execute_print(self, node: ASTNode) -> None:
        value = self.execute_node(node.children[0])
        print(value)

    def execute_binary_op(self, node: ASTNode) -> Any:
        left = self.execute_node(node.children[0])
        right = self.execute_node(node.children[1])
        
        if isinstance(left, str) and isinstance(right, str):
            operations = {
                TokenType.EQUAL: lambda x, y: x == y,
                TokenType.GREATER: lambda x, y: x > y,
                TokenType.LESS: lambda x, y: x < y,
            }
        else:
            if isinstance(left, str):
                try:
                    left = int(left)
                except ValueError:
                    pass
            if isinstance(right, str):
                try:
                    right = int(right)
                except ValueError:
                    pass
            
            operations = {
                TokenType.PLUS: lambda x, y: int(x) + int(y),
                TokenType.MINUS: lambda x, y: int(x) - int(y),
                TokenType.MULTIPLY: lambda x, y: int(x) * int(y),
                TokenType.DIVIDE: lambda x, y: int(int(x) / int(y)) if int(y) != 0 else RuntimeError("Division by zero"),
                TokenType.GREATER: lambda x, y: int(x) > int(y),
                TokenType.LESS: lambda x, y: int(x) < int(y),
                TokenType.EQUAL: lambda x, y: int(x) == int(y),
                TokenType.AND: lambda x, y: bool(x) and bool(y),
                TokenType.OR: lambda x, y: bool(x) or bool(y),
            }
        
        operation = operations.get(node.value)
        if not operation:
            raise RuntimeError(f"Unknown operator: {node.value}")
        
        return operation(left, right)

    def execute_if(self, node: ASTNode) -> None:
        condition = self.execute_node(node.children[0])
        
        if condition:
            self.push_scope()
            result = self.execute_node(node.children[1])
            self.pop_scope()
        elif len(node.children) > 2: 
            self.push_scope()
            result = self.execute_node(node.children[2])
            self.pop_scope()

    def execute_while(self, node: ASTNode) -> None:
        condition = self.execute_node(node.children[0])
        while condition:
            if isinstance(node.children[1], ASTNode) and node.children[1].type == 'block':
                for stmt in node.children[1].children:
                    self.execute_node(stmt)
            else:
                self.execute_node(node.children[1])
            condition = self.execute_node(node.children[0])

    def execute_for(self, node: ASTNode) -> None:
        self.execute_node(node.children[0])
        
        var_name = node.value['var']
        
        while True:
            if not self.execute_node(node.children[1]):
                break
                
            if isinstance(node.children[3], ASTNode) and node.children[3].type == 'block':
                for stmt in node.children[3].children:
                    self.execute_node(stmt)
            
            new_value = self.execute_node(node.children[2])
            
            if var_name in self.variables:
                self.variables[var_name] = new_value
            else:
                for scope in reversed(self.current_scope):
                    if var_name in scope:
                        scope[var_name] = new_value
                        break

    def execute_method_definition(self, node: ASTNode) -> None:
        func_name = node.value
        parameters = node.children[0].children
        body = node.children[1].children
        self.functions[func_name] = Function(func_name, parameters, body)

    def execute_function_call(self, node: ASTNode) -> Any:
        func_name = node.value['function']
        if func_name not in self.functions:
            raise RuntimeError(f"Undefined function: {func_name}")
        
        func = self.functions[func_name]
        args = [self.execute_node(arg) for arg in node.children]
        
        self.push_scope()
        
        for param, arg in zip(func.parameters, args):
            self.variables[param.value['name']] = arg
        
        result = None
        for stmt in func.body:
            result = self.execute_node(stmt)
            if self.return_value is not None:
                result = self.return_value
                self.return_value = None
                break
        
        self.pop_scope()
        return result

    def execute_method_call(self, node: ASTNode) -> Any:
        object_name = node.value['object']
        method = node.value['method']
        
        if object_name in self.stacks:
            stack = self.stacks[object_name]
            if method == 'push':
                value = self.execute_node(node.children[0])
                stack.append(value)
                return None
            elif method == 'pop':
                if not stack:
                    raise RuntimeError(f"Stack '{object_name}' is empty")
                return stack.pop()
        
        elif object_name in self.queues:
            queue = self.queues[object_name]
            if method == 'add':
                value = self.execute_node(node.children[0])
                queue.append(value)
                return None
            elif method == 'remove':
                if not queue:
                    raise RuntimeError(f"Queue '{object_name}' is empty")
                return queue.popleft()
                
        raise RuntimeError(f"Unknown object '{object_name}' or method '{method}'")

    def execute_return(self, node: ASTNode) -> Any:
        self.return_value = self.execute_node(node.children[0])
        return self.return_value

    def execute_ternary_op(self, node: ASTNode) -> Any:
        condition = self.execute_node(node.children[0])
        if condition:
            return self.execute_node(node.children[1])
        else:
            return self.execute_node(node.children[2])

    def execute_array_declaration(self, node: ASTNode) -> None:
        array_name = node.value['name']
        elements = [self.execute_node(elem) for elem in node.children]
        self.arrays[array_name] = elements

    def execute_array_access(self, node: ASTNode) -> Any:
        array_name = node.value['array']
        if array_name not in self.arrays:
            raise RuntimeError(f"Undefined array: {array_name}")
            
        index = self.execute_node(node.children[0])
        if not isinstance(index, int):
            raise RuntimeError(f"Array index must be an integer, got {type(index)}")
            
        array = self.arrays[array_name]
        if index < 0 or index >= len(array):
            raise RuntimeError(f"Array index {index} out of bounds for array of size {len(array)}")
            
        return array[index]

    def execute_array_assignment(self, node: ASTNode) -> None:
        array_name = node.value['array']
        if array_name not in self.arrays:
            raise RuntimeError(f"Undefined array: {array_name}")
            
        index = self.execute_node(node.children[0])
        value = self.execute_node(node.children[1])
        
        if not isinstance(index, int):
            raise RuntimeError(f"Array index must be an integer, got {type(index)}")
            
        array = self.arrays[array_name]
        if index < 0 or index >= len(array):
            raise RuntimeError(f"Array index {index} out of bounds for array of size {len(array)}")
            
        array[index] = value

    def execute_string_operation(self, node: ASTNode) -> str:
        value = str(self.execute_node(node.children[0]))
        operation = node.value['operation']
        
        if operation == TokenType.UPPER:
            return value.upper()
        elif operation == TokenType.LOWER:
            return value.lower()
        elif operation == TokenType.JOIN:
            return ''.join(value)
        
        raise RuntimeError(f"Unknown string operation: {operation}")

    def execute_input(self, node: ASTNode) -> str:
        if node.value and 'prompt' in node.value:
            print(node.value['prompt'], end='', flush=True)
            self.last_input = input()
            return self.last_input
        return self.last_input if self.last_input is not None else input()

    def execute_input_expression(self, node: ASTNode) -> Any:
        if self.last_input is not None:
            value = self.last_input
            self.last_input = None
        else:
            value = input()

        expected_type = node.value.get('expected_type') if node.value else None

        if expected_type == TokenType.TYPE_STRING:
            return str(value)  
        elif expected_type == TokenType.TYPE_BOOL:
            if value.lower() in ['true', '1']:
                return 1
            elif value.lower() in ['false', '0']:
                return 0
            raise RuntimeError(f"Invalid boolean input: expected true/false or 1/0, got '{value}'")
        else: 
            try:
                return int(value)
            except ValueError:
                raise RuntimeError(f"Invalid input: expected a number, got '{value}'")

    def execute_declaration(self, node: ASTNode) -> None:
        var_name = node.value['identifier']
        var_type = node.value['type']
        
        if node.children:
            value = self.execute_node(node.children[0])
            self.variables[var_name] = value
        else:
            default = "" if var_type == TokenType.TYPE_STRING else 0
            self.variables[var_name] = default

    def execute_data_structure_declaration(self, node: ASTNode) -> None:
        struct_type = node.value['type']
        name = node.value['name']
        
        if struct_type == TokenType.STACK:
            self.stacks[name] = []
        elif struct_type == TokenType.QUEUE:
            self.queues[name] = deque()

    def execute_block(self, node: ASTNode) -> Any:
        result = None
        if node.children:
            self.push_scope()
            for stmt in node.children:
                result = self.execute_node(stmt)
                if self.return_value is not None:
                    break
            self.pop_scope()
        return result

    def get_variable(self, name: str) -> Any:
        if name in self.constants:
            return self.constants[name]
        if name in self.variables:
            return self.variables[name]
        
        for scope in reversed(self.current_scope):
            if name in scope:
                return scope[name]
                
        raise RuntimeError(f"Undefined variable: {name}")
