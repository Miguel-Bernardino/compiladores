from Token.Token import Token
from Token.TokenType import TokenType
from Symbol.SymbolTable import SymbolTable

class LexerScanner:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        
        # Conjunto de palavras reservadas (Set em Python é O(1) para busca)
        self.reserved_words = {"if", "else", "while", "return", "int", "float"}
        self.symbol_table = SymbolTable()

    def advance(self):
        """Avança o ponteiro de leitura em 1 caractere, controlando linha e coluna."""
        if self.position < len(self.source_code):
            if self.source_code[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

    def skip_whitespace(self):
        """Ignora espaços, quebras de linha e tabulações."""
        while self.position < len(self.source_code) and self.source_code[self.position].isspace():
            self.advance()

    def recognize_identifier_or_keyword(self) -> Token:
        """Monta o lexema e decide se é Palavra Reservada ou Identificador."""
        start_column = self.column
        start_line = self.line
        lexeme_chars = []

        # Acumula enquanto for letra ou número (ex: contador123)
        while self.position < len(self.source_code) and self.source_code[self.position].isalnum():
            lexeme_chars.append(self.source_code[self.position])
            self.advance()

        # Junta a lista de caracteres em uma string final
        lexeme = "".join(lexeme_chars)

        # 1. Verifica se está na lista de Palavras Reservadas
        if lexeme in self.reserved_words:
            return Token(TokenType.RESERVED_WORD, lexeme, start_line, start_column)

        # 2. Se não for, é um Identificador. Inserimos/Buscamos na Tabela de Símbolos!
        symbol = self.symbol_table.get_or_add(lexeme, start_line, start_column)
        
        return Token(TokenType.IDENTIFIER, symbol.lexeme, start_line, start_column)

    def get_next_token(self) -> Token:
        """Método principal que o Parser chamará para pedir o próximo átomo."""
        self.skip_whitespace()

        # Verifica fim do arquivo
        if self.position >= len(self.source_code):
            return Token(TokenType.EOF, "EOF", self.line, self.column)

        current_char = self.source_code[self.position]

        # Inicia reconhecimento: Se começa com letra, é identificador ou palavra reservada
        if current_char.isalpha():
            return self.recognize_identifier_or_keyword()

        # (Aqui você adicionaria ifs para char.isdigit() para Números e operadores/delimitadores)
        
        # Caractere desconhecido/inválido: Erro Léxico
        error_token = Token(TokenType.ERROR, current_char, self.line, self.column)
        self.advance()
        return error_token