from dataclasses import dataclass

@dataclass
class SymbolInfo:
    lexeme: str
    first_line: int
    first_column: int