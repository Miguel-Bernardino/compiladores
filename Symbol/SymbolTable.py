from Symbol.Symbolnfo import SymbolInfo

# Class wich represents a symbol table, which is a data structure used to store and manage symbols (identifiers) in a programming language. It provides methods to add new symbols, retrieve existing symbols, and get all symbols in the table.
class SymbolTable:
    def __init__(self):
        # using a dictionary to store symbols, where the keys are the lexemes (identifiers) and the values are instances of SymbolInfo containing information about each symbol.
        self._table = {}

    # Method to add a new symbol to the table or retrieve an existing one based on its lexeme.
    def get_or_add(self, lexeme: str, line: int, column: int) -> SymbolInfo:
        # if the lexeme already exists in the symbol table, return the existing SymbolInfo instance
        if lexeme in self._table:
            return self._table[lexeme]
        
        # if it doesn't exist, create a new SymbolInfo instance, add it to the table, and return it
        new_symbol = SymbolInfo(lexeme, line, column)
        self._table[lexeme] = new_symbol
        return new_symbol

    def get_all_symbols(self):
        return list(self._table.values())