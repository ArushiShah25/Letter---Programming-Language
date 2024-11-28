# SER502-Letter

# Team-3
- Arushi Ashish Shah
- Pradyumn Mohta
- Pavan kalyan Lingutla


# Description
 Letter is a minimalistic, single-letter syntax language designed for efficient and compact code expression. Each command or keyword is represented by a single uppercase letter, reducing verbosity, increasing speed, and making the language intuitive for those familiar with foundational programming constructs. The language supports comprehensive programming features while maintaining simplicity in syntax.

## Features

Basic Types and Variables:

- Integer (T): Whole number values
- String (S): Text values
- Boolean: Represented using integers (0 and 1)

Arithmetic Operations

- Addition (+)
- Subtraction (-)
- Multiplication (*)
- Division (/)

Control Structures

- If-Else (I, E): Conditional branching
- While Loop (W): Conditional looping
- For Loop (F): Iterative looping

Functions

- Function Declaration (M): Method/Function definition
- Return Statement (R): Return values from functions
- Function Parameters: Support for multiple parameters

Data Structures

- Arrays (A): Support for integer and string arrays
- Stack (K): Last-In-First-Out data structure
- Queue (Q): First-In-First-Out data structure

String Operations

- Uppercase (U): Convert string to uppercase
- Lowercase (L): Convert string to lowercase
- String Comparison: Using = operator

Additional Features

- Constants (C): Immutable values
- Input Operations (N): Read user input
- Print Statement (P): Output values
- Ternary Operator (?:): Conditional expressions
- Comments: Single-line (#) and multi-line (#* *#)

## Implementation
The compiler/interpreter is implemented in Python and consists of three main components:

1. Lexer (lexer_parser.py):

- Tokenizes source code
- Handles language syntax
- Processes comments


2. Parser (lexer_parser.py):

- Builds Abstract Syntax Tree (AST)
- Validates syntax
- Manages operator precedence


3. Runtime (runtime.py):

- Executes the AST
- Manages memory and scope
- Handles operations
- Provides error handling

## Installation and Setup

- Clone the repository
- No additional dependencies required
- Run using Python 3.x

## Build and Execution Instructions
- To run a program:
python main.py < filename >

- Example:
python main.py test_program.txt

## Test Files
The repository includes comprehensive test files for each feature:

- test_arithmetic.txt: Basic operations and variables
- test_strings.txt: String operations and comparisons
- test_control_flow.txt: If-else, loops
- test_functions.txt: Function definitions and calls
- test_arrays.txt: Array operations
- test_stack.txt: Stack operations
- test_queue.txt: Queue operations
- test_constants.txt: Constant declarations
- test_io.txt: Input/Output operations
- test_ternary.txt: Ternary operator
  
## Error Handling
The interpreter includes error checking for:

- Syntax errors
- Runtime errors
- Type mismatches
- Undefined variables
- Array bounds
- Invalid operations


## Youtube Link (Presentation):- 
https://youtu.be/MnZCXvdwcr4
