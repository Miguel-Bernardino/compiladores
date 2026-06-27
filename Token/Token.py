from dataclasses import dataclass
from Token.TokenType import TokenType

@dataclass
class Token:
    type:               TokenType
    lexeme:             str
    line:               int
    column:             int
    atom_code:          int = 0     # ex: 0xA15, 0xB04, 0xC01
    symbol_table_index: int = -1    # -1 = não armazenado