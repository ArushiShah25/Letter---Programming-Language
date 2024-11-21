# main.py

import sys
from lexer_parser import parse_program, print_program_ast
from runtime import Runtime

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <source_file>")
        print("Example: python main.py program.txt")
        sys.exit(1)
    
    # Read source file
    source_file = sys.argv[1]
    try:
        with open(source_file, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{source_file}' not found")
        sys.exit(1)
    
    try:
        # Parse the code to get AST
        ast = parse_program(source_code)
        
        """ Print the AST
        print("\nGenerated AST:")
        print_program_ast(ast)""" 
        
        # Execute the code
        print("\nProgram Output:")
        print("=" * 20)
        runtime = Runtime()
        runtime.execute(ast)
        print("=" * 20)
        
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
