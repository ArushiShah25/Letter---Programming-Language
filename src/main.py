from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Any

class TokenType(Enum):
    # Types
    TYPE_INT = 'T'
    TYPE_BOOL = 'B'
    TYPE_STRING = 'S'
    
    # Keywords
    PRINT = 'P'
    IF = 'I'
    ELSE = 'E'
    FOR = 'F'
    WHILE = 'W'
    
    # Operators
    PLUS = '+'
    MINUS = '-'
    MULTIPLY = '*'
    DIVIDE = '/'
    
    # Boolean operators
    AND = '&'
    OR = '|'
    NOT = '!'
    
    # Relational operators
    GREATER = '>'
    LESS = '<'
    EQUAL = '='
    
    # Special characters
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'    # Added curly braces
    RBRACE = '}'    # Added curly braces
    SEMICOLON = ';'
    QUESTION = '?'
    COLON = ':'
    
    # Other
    IDENTIFIER = 'IDENTIFIER'
    INTEGER_LITERAL = 'INTEGER_LITERAL'
    STRING_LITERAL = 'STRING_LITERAL'
    BOOLEAN_LITERAL = 'BOOLEAN_LITERAL'

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    position: int

@dataclass
class ASTNode:
    type: str
    value: Any = None
    children: List['ASTNode'] = None

class Lexer:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.current_char = self.source_code[0] if source_code else None
    
    def advance(self):
        self.position += 1
        if self.position >= len(self.source_code):
            self.current_char = None
        else:
            self.current_char = self.source_code[self.position]
            if self.current_char == '\n':
                self.line += 1
    
    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def read_identifier(self) -> Token:
        identifier = ''
        start_pos = self.position
        
        while self.current_char and self.current_char.isalnum():
            identifier += self.current_char
            self.advance()
        
        # Check if it's a single-letter keyword
        for token_type in TokenType:
            if token_type.value == identifier:
                return Token(token_type, identifier, self.line, start_pos)
        
        return Token(TokenType.IDENTIFIER, identifier, self.line, start_pos)
    
    def read_number(self) -> Token:
        number = ''
        start_pos = self.position
        
        while self.current_char and self.current_char.isdigit():
            number += self.current_char
            self.advance()
        
        return Token(TokenType.INTEGER_LITERAL, number, self.line, start_pos)
    
    def read_string(self) -> Token:
        string = ''
        start_pos = self.position
        self.advance()  # Skip the opening quote
        
        while self.current_char and self.current_char != '"':
            string += self.current_char
            self.advance()
        
        if self.current_char == '"':
            self.advance()  # Skip the closing quote
        
        return Token(TokenType.STRING_LITERAL, string, self.line, start_pos)
    
    def get_next_token(self) -> Optional[Token]:
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char.isalpha():
                return self.read_identifier()
            
            if self.current_char.isdigit():
                return self.read_number()
            
            if self.current_char == '"':
                return self.read_string()
            
            # Handle operators and special characters
            current_char = self.current_char
            current_pos = self.position
            self.advance()
            
            # Map single characters to token types
            char_to_token = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '&': TokenType.AND,
                '|': TokenType.OR,
                '!': TokenType.NOT,
                '>': TokenType.GREATER,
                '<': TokenType.LESS,
                '=': TokenType.EQUAL,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,  # Added
                '}': TokenType.RBRACE,  # Added
                ';': TokenType.SEMICOLON,
                '?': TokenType.QUESTION,
                ':': TokenType.COLON
            }
            
            if current_char in char_to_token:
                return Token(char_to_token[current_char], current_char, self.line, current_pos)
            
            raise SyntaxError(f"Unknown character '{current_char}' at line {self.line}, position {current_pos}")
        
        return None

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def consume(self, token_type: TokenType):
        if self.current_token and self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token}")
    
    def parse_statement(self) -> ASTNode:
        if not self.current_token:
            return None
        
        if self.current_token.type == TokenType.PRINT:
            return self.parse_print_statement()
        elif self.current_token.type == TokenType.IF:
            return self.parse_if_statement()
        elif self.current_token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif self.current_token.type == TokenType.FOR:  
            return self.parse_for_statement()
        elif self.current_token.type in [TokenType.TYPE_INT, TokenType.TYPE_BOOL, TokenType.TYPE_STRING]:
            return self.parse_declaration()
        else:
            return self.parse_expression()
    
    def parse_block(self) -> List[ASTNode]:
        statements = []
        self.consume(TokenType.LBRACE)
        
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
                
        self.consume(TokenType.RBRACE)
        return statements
    
    def parse_print_statement(self) -> ASTNode:
        self.consume(TokenType.PRINT)
        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        return ASTNode('print', children=[expr])
    
    def parse_if_statement(self) -> ASTNode:
        self.consume(TokenType.IF)
        self.consume(TokenType.LPAREN)
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN)
        
        then_stmt = ASTNode('block', children=self.parse_block())
        
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.consume(TokenType.ELSE)
            else_stmt = ASTNode('block', children=self.parse_block())
            return ASTNode('if', children=[condition, then_stmt, else_stmt])
        
        return ASTNode('if', children=[condition, then_stmt])

    def parse_for_statement(self) -> ASTNode:
        self.consume(TokenType.FOR)
        self.consume(TokenType.LPAREN)
        
        init = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        
        condition = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        
        update = self.parse_expression()
        self.consume(TokenType.RPAREN)
        
        body = self.parse_block()
    
        return ASTNode('for', children=[init, condition, update, ASTNode('block', children=body)])

    def parse_while_statement(self) -> ASTNode:
        self.consume(TokenType.WHILE)
        self.consume(TokenType.LPAREN)
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN)
        body = ASTNode('block', children=self.parse_block())
        return ASTNode('while', children=[condition, body])
    
    def parse_declaration(self) -> ASTNode:
        type_token = self.current_token
        self.current_token = self.lexer.get_next_token()
        
        identifier = self.current_token.value
        self.consume(TokenType.IDENTIFIER)
        
        if self.current_token.type == TokenType.EQUAL:
            self.consume(TokenType.EQUAL)
            value = self.parse_expression()
            self.consume(TokenType.SEMICOLON)
            return ASTNode('declaration', value={'type': type_token.type, 'identifier': identifier}, children=[value])
        
        self.consume(TokenType.SEMICOLON)
        return ASTNode('declaration', value={'type': type_token.type, 'identifier': identifier})
    
    def parse_expression(self) -> ASTNode:
        left = self.parse_term()
        
        while self.current_token and self.current_token.type in [
            TokenType.PLUS, TokenType.MINUS, TokenType.GREATER, TokenType.LESS, 
            TokenType.EQUAL, TokenType.AND, TokenType.OR
        ]:
            operator = self.current_token.type
            self.current_token = self.lexer.get_next_token()
            right = self.parse_term()
            left = ASTNode('binary_op', value=operator, children=[left, right])
        
        return left
    
    def parse_term(self) -> ASTNode:
        left = self.parse_factor()
        
        while self.current_token and self.current_token.type in [TokenType.MULTIPLY, TokenType.DIVIDE]:
            operator = self.current_token.type
            self.current_token = self.lexer.get_next_token()
            right = self.parse_factor()
            left = ASTNode('binary_op', value=operator, children=[left, right])
        
        return left
    
    def parse_factor(self) -> ASTNode:
        token = self.current_token
        
        if token.type == TokenType.INTEGER_LITERAL:
            self.current_token = self.lexer.get_next_token()
            return ASTNode('integer_literal', value=int(token.value))
        elif token.type == TokenType.STRING_LITERAL:
            self.current_token = self.lexer.get_next_token()
            return ASTNode('string_literal', value=token.value)
        elif token.type == TokenType.BOOLEAN_LITERAL:
            self.current_token = self.lexer.get_next_token()
            return ASTNode('boolean_literal', value=token.value.lower() == 'true')
        elif token.type == TokenType.IDENTIFIER:
            self.current_token = self.lexer.get_next_token()
            return ASTNode('identifier', value=token.value)
        elif token.type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN)
            return expr
        elif token.type == TokenType.NOT:
            self.current_token = self.lexer.get_next_token()
            factor = self.parse_factor()
            return ASTNode('unary_op', value=TokenType.NOT, children=[factor])
        
        raise SyntaxError(f"Unexpected token {token}")
    
    def parse(self) -> List[ASTNode]:
        statements = []
        while self.current_token:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements

def print_ast(node: ASTNode, indent: int = 0) -> None:
    """Pretty print the AST with proper indentation."""
    indent_str = "  " * indent
    
    if not node:
        return
    
    # Print node type
    print(f"{indent_str}Type: {node.type}")
    
    # Print node value if it exists
    if node.value is not None:
        print(f"{indent_str}Value: {node.value}")
    
    # Recursively print children
    if node.children:
        print(f"{indent_str}Children:")
        for child in node.children:
            print_ast(child, indent + 1)

def print_program_ast(ast_nodes: List[ASTNode]) -> None:
    """Print the entire program's AST."""
    print("Program AST:")
    print("===========")
    for i, node in enumerate(ast_nodes, 1):
        print(f"\nStatement {i}:")
        print_ast(node)
        print("-" * 40)

def parse_program(source_code: str) -> List[ASTNode]:
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    return parser.parse()

import sys

def read_file(filename: str) -> str:
    """Read source code from a file."""
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def main():
    # Check if filename is provided as command line argument
    if len(sys.argv) != 2:
        print("Usage: python parser.py <filename>")
        print("Example: python parser.py program.txt")
        sys.exit(1)
    
    filename = sys.argv[1]
    source_code = read_file(filename)
    
    try:
        ast = parse_program(source_code)
        print_program_ast(ast)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
