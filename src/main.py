import sys

# Define token types
class Token:
    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def __repr__(self):
        return f'Token({self.token_type}, {repr(self.value)})'

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.token_type == other.token_type and self.value == other.value
        return False

    def __hash__(self):
        return hash((self.token_type, self.value))


# Tokenizer class
class Tokenizer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0
        self.current_char = self.source_code[self.position] if self.source_code else None

    def error(self, message=""):
        raise SyntaxError(f"Invalid character at position {self.position}. {message}")

    def advance(self):
        self.position += 1
        if self.position < len(self.source_code):
            self.current_char = self.source_code[self.position]
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def variable(self):
        result = self.current_char
        self.advance()
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return Token('IDENTIFIER', result)

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return Token('INTEGER', result)

    def string(self):
        self.advance()  # skip opening quote
        result = ''
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()
        self.advance()  # skip closing quote
        return Token('STRING', result)

    def tokenize(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.islower() or self.current_char == '_':
                tokens.append(self.variable())
                continue
            if self.current_char.isdigit():
                tokens.append(self.integer())
                continue
            if self.current_char == '"':
                tokens.append(self.string())
                continue

            # Handle single-character and compound tokens
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token('EQ', '=='))
                    self.advance()
                else:
                    tokens.append(Token('ASSIGN', '='))
            elif self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token('LE', '<='))
                    self.advance()
                else:
                    tokens.append(Token('LT', '<'))
            elif self.current_char == ';':
                tokens.append(Token('SEMICOLON', ';'))
            elif self.current_char == '?':
                tokens.append(Token('TERNARY', '?'))
            elif self.current_char == ':':
                tokens.append(Token('TERNARY', ':'))
            elif self.current_char == '+':
                self.advance()
                if self.current_char == '+':
                    tokens.append(Token('INCREMENT', '++'))
                    self.advance()  # Skip the second '+'
                else:
                    tokens.append(Token('ADD', '+'))
                continue
            elif self.current_char == ',':
                tokens.append(Token('COMMA', ','))
            elif self.current_char == '(':
                tokens.append(Token('LPAREN', '('))
            elif self.current_char == ')':
                tokens.append(Token('RPAREN', ')'))
            elif self.current_char in {'T', 'B', 'S'}:  # Add type keywords
                tokens.append(Token('TYPE', self.current_char))
            elif self.current_char == 'P':  # Print statement
                tokens.append(Token('PRINT', 'P'))
            elif self.current_char == 'I':  # If statement
                tokens.append(Token('IF', 'I'))
            elif self.current_char == 'E':  # Else statement
                tokens.append(Token('ELSE', 'E'))
            else:
                self.error(f"Unexpected character: {self.current_char}")

            self.advance()
        return tokens


# Define AST nodes
class Num:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'Num({self.value})'


class VarDecl:
    def __init__(self, var_type, variable, value):
        self.var_type = var_type
        self.variable = variable
        self.value = value

    def __repr__(self):
        return f'VarDecl({self.var_type}, {self.variable}, {repr(self.value)})'


class Print:
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f'Print({self.expression})'


class IfStatement:
    def __init__(self, condition, true_branch, false_branch=None):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __repr__(self):
        return f'If({self.condition}, {self.true_branch}, {self.false_branch})'


# Parser class
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = self.tokens[0] if self.tokens else None
        self.position = 0

    def error(self, message=""):
        raise SyntaxError(f"Invalid syntax at position {self.position}. {message}")

    def advance(self):
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None

    def parse(self):
        statements = []
        while self.current_token is not None:
            if self.current_token.token_type == 'TYPE':
                # Handle T, B, S
                var_decl = self.variable_decl()
                statements.append(var_decl)
            elif self.current_token.token_type == 'PRINT':
                statements.append(self.parse_print_statement())
            elif self.current_token.token_type == 'IF':
                statements.append(self.parse_if_statement())
            else:
                self.error("Unexpected token")

            if self.current_token is not None and self.current_token.token_type == 'SEMICOLON':
                self.advance()  # Move past semicolon

        return statements

    def variable_decl(self):
        var_type = self.current_token.value
        self.advance()  # Move past type keyword (T, B, S)
        if self.current_token.token_type != 'IDENTIFIER':
            self.error("Expected identifier")
        variable = self.current_token.value
        self.advance()  # Move past identifier
        if self.current_token.token_type != 'ASSIGN':
            self.error("Expected assignment operator")
        self.advance()  # Move past assign token
        # Check if the next token is a string or integer
        if self.current_token.token_type == 'STRING':
            value = self.string()
        elif self.current_token.token_type == 'INTEGER':
            value = self.num()
        else:
            self.error("Unexpected value type")
        return VarDecl(var_type, variable, value)

    def parse_print_statement(self):
        self.advance()  # Skip 'P'
        expression = self.current_token.value
        self.advance()  # Move past the expression
        return Print(expression)

    def parse_if_statement(self):
        self.advance()  # Skip 'I'
        condition = self.parse_expression()  # Parse condition
        true_branch = self.parse()  # Parse true branch statement
        false_branch = None
        if self.current_token.token_type == 'ELSE':
            self.advance()  # Skip 'E'
            false_branch = self.parse()  # Parse false branch
        return IfStatement(condition, true_branch, false_branch)

    def string(self):
        if self.current_token.token_type != 'STRING':
            self.error("Expected a string")
        value = self.current_token.value
        self.advance()  # Move past string
        return value

    def num(self):
        if self.current_token.token_type != 'INTEGER':
            self.error("Expected an integer")
        value = Num(self.current_token.value)
        self.advance()  # Move past integer
        return value

    def parse_expression(self):
        # Basic implementation; expand as needed
        if self.current_token.token_type == 'IDENTIFIER':
            expr = self.current_token.value
            self.advance()
            return expr
        elif self.current_token.token_type == 'INTEGER':
            return self.num()
        else:
            self.error("Expected an expression")


def run_file(file_path):
    with open(file_path, 'r') as file:
        source_code = file.read()

    # Tokenizing the source code
    tokenizer = Tokenizer(source_code)
    tokens = tokenizer.tokenize()
    print("Tokens:", tokens)

    # Parsing the tokens
    parser = Parser(tokens)
    parse_tree = parser.parse()
    print("Parse Tree:", parse_tree)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <source_code_file>")
    else:
        run_file(sys.argv[1])
