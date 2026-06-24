from enum import Enum

# 1. Defining the TokenType Enum to represent different types of tokens in a programming language.
class TokenType(Enum):
    RESERVED_WORD        = "A"
    RESERVED_SYMBOL      = "B"
    RESERVED_IDENTIFIER  = "C"
    SUBMACHINE           = "D"