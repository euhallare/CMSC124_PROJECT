# LOLCODE Interpreter

A complete LOLCODE interpreter developed for **CMSC 124 - S-3L (Group EJDB)**. It provides both a graphical desktop environment and command-line tools for lexing, parsing, and executing `.lol` programs.

## Features

- Tkinter-based GUI with source editor, file browser, console, token table, and live symbol table
- Lexical analysis of LOLCODE keywords, identifiers, literals, comments, separators, and errors
- Recursive-descent parsing with abstract syntax tree (AST) generation
- Runtime interpretation and symbol-table updates
- Variable declaration and reassignment
- Numeric, YARN, TROOF, NOOB, and BUKKIT values
- Explicit and implicit type casting
- Arithmetic and comparison operations
- Boolean operations and variadic expressions
- `IF/ELSE`, `MEBBE`, `WTF?` switch statements, and loops
- Functions with parameters, arguments, and return values
- Console input through `GIMMEH`
- Inline `BTW` comments and block `OBTW`/`TLDR` comments
- Soft line breaks, line continuation, YARN escape sequences, and arrays/BUKKIT slots

## Project Structure

```text
CMSC124_PROJECT/
├── "source code"/
│   ├── gui.py             # Tkinter graphical application
│   ├── lexer/
│   │   ├── lexer.py       # Lexical analyzer
│   │   └── tokens.py      # Token types and language keywords
│   ├── parser/
│   │   ├── parser.py      # Recursive-descent parser
│   │   └── nodes.py       # AST node definitions
│   ├── interpreter/
│   │   ├── interpreter.py # AST executor
│   │   ├── environment.py # Variable and symbol-table environment
│   │   ├── typecasting.py # LOLCODE type conversion
│   │   ├── values.py      # Runtime value types
│   │   └── signals.py     # Return and loop-control signals
│   ├── given_test/        # Provided base test programs
│   └── additional_test/   # Additional feature and edge-case tests
├── bonus/                 # Bonus specification test programs
├── own_test/              # Custom team test programs
├── own_bonus/             # Custom bonus test programs
└── README.md
```

## Requirements

- Python 3.10 or newer
- Tkinter

Tkinter is included with most Python installations. On Ubuntu/Debian-based Linux systems, it may be installed with:

```bash
sudo apt install python3-tk
```

The interpreter does not require third-party Python packages.

## Running the GUI

From the project root:

```bash
python3 "source code"/gui.py
```

The GUI lets you:

1. Open an existing `.lol` file or create text in the editor.
2. View lexemes and token classifications.
3. Execute the program and inspect runtime output.
4. Monitor declared variables in the symbol table.
5. Enter values for `GIMMEH` statements in the input bar.
6. Save changes to the current file or choose a new file.

You can also open the project root with the built-in file browser and navigate directories normally.

## Running from the Terminal

Execute a LOLCODE program:

```bash
cd "source code"
python3 -m interpreter.interpreter given_test/01_variables.lol
```

Tokenize and display the lexemes:

```bash
cd "source code"
python3 -m lexer.lexer given_test/01_variables.lol
```

Parse and display the syntax tree:

```bash
cd "source code"
python3 -m parser.parser given_test/01_variables.lol
```

## Example Program

```lol
HAI
    WAZZUP
        I HAS A name ITZ "World"
        I HAS A num ITZ 10
    BUHBYE

    VISIBLE "Hello, " + name
    VISIBLE SUM OF num AN 5
KTHXBYE
```

## Test Programs

The repository includes several groups of `.lol` programs:

- `"source code"/given_test/` - Required baseline interpreter tests
- `"source code"/additional_test/` - Supplemental syntax and edge-case tests
- `bonus/` - Standard bonus feature tests
- `own_test/` - Team-created test programs
- `own_bonus/` - Team-created bonus programs

Run a test file with the GUI or through the interpreter CLI:

```bash
cd "source code"
python3 -m interpreter.interpreter given_test/10_functions.lol
python3 -m interpreter.interpreter ../bonus/ec08_array.lol
```

## Supported LOLCODE Concepts

The implementation covers core LOLCODE constructs including:

- Program boundaries: `HAI` / `KTHXBYE`
- Declarations: `I HAS A`
- Variable declarations block: `WAZZUP` / `BUHBYE`
- Output and input: `VISIBLE` / `GIMMEH`
- Assignment: `R`
- Type casting: `MAEK` and `IS NOW A`
- Arithmetic: `SUM OF`, `DIFF OF`, `PRODUKT OF`, `QUOSHUNT OF`, `MOD OF`
- Extrema: `BIGGR OF`, `SMALLR OF`
- Boolean: `BOTH OF`, `EITHER OF`, `WON OF`, `NOT`
- Comparison: `BOTH SAEM`, `DIFFRINT`
- Variadic expressions: `ALL OF`, `ANY OF`, `SMOOSH`
- Conditional statements: `O RLY?`, `YA RLY`, `MEBBE`, `NO WAI`, `OIC`
- Switch statements: `WTF?`, `OMG`, `OMGWTF`
- Loops: `IM IN YR` / `IM OUTTA YR`, `UPPIN`, `NERFIN`, `WILE`, `TIL`
- Functions: `HOW IZ I`, `I IZ`, `YR`, `FOUND YR`
- Flow control: `GTFO`
- Arrays: `BUKKIT`, `HAS A`, and `'Z` slot access
