from dataclasses import dataclass
import TokenType

@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int