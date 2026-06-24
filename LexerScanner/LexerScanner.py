from Reserved import ReservedSymbols, ReservedWords
from Reserved.Reserved_Identifiers import ReservedIdentifiers
from Token.Token import Token
from Token.TokenType import TokenType
from Symbol.SymbolTable import SymbolTable

class LexerScanner:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.symbol_table = SymbolTable()

        self.reserved_words = ReservedWords()
        self.reserved_symbols = ReservedSymbols()
        self.reserved_identifiers = ReservedIdentifiers()

    def advance(self):
        if self.position < len(self.source_code):
            if self.source_code[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

    def skip_whitespace(self):
        while self.position < len(self.source_code) and self.source_code[self.position].isspace():
            self.advance()

    def recognize_identifier_or_keyword(self) -> Token:
        start_column = self.column
        start_line = self.line
        lexeme_chars = []

        # Acumulate characters while they are alphanumeric (letters or digits)
        while self.position < len(self.source_code) and self.source_code[self.position].isalnum():
            lexeme_chars.append(self.source_code[self.position])
            self.advance()

        # join the characters to form the lexeme
        lexeme = "".join(lexeme_chars)

        # 1. Check if the lexeme is a reserved word
        if lexeme in self.reserved_words:
            return Token(TokenType.RESERVED_WORD, lexeme, start_line, start_column)
        elif lexeme in self.reserved_identifiers:
            return Token(TokenType.RESERVED_IDENTIFIER, lexeme, start_line, start_column)
        elif lexeme in self.reserved_symbols:
            return Token(TokenType.RESERVED_SYMBOL, lexeme, start_line, start_column)

        symbol = self.symbol_table.get_or_add(lexeme, start_line, start_column)
        
        

    def get_next_token(self) -> Token | None:
        self.skip_whitespace()

        # check EOF
        if self.position >= len(self.source_code):
            return None;

        current_char = self.source_code[self.position]

        # Start recognizing identifiers or keywords
        if current_char.isalpha():
            return self.recognize_identifier_or_keyword()

        # (Here you would add ifs for char.isdigit() for Numbers and operators/delimiters)
        
        self.advance()
        return None