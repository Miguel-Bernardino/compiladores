from Symbol.Symbolnfo import SymbolInfo


class SymbolTable:
    """
    Stores and manages identifier symbols found during lexical analysis.

    Only identifier atoms (C-codes: variable, functionName, programName,
    stringConst, charConst, intConst, realConst) are stored here.
    Reserved words (A-codes) and reserved symbols (B-codes) are never added.

    Each unique lexeme gets exactly one entry; repeated occurrences just
    update the line-occurrence list of the existing entry.
    """

    def __init__(self):
        # Primary store: lexeme → SymbolInfo
        self._table: dict[str, SymbolInfo] = {}
        # Insertion-order index counter (1-based, as shown in the spec .TAB example)
        self._next_index: int = 1

    def get_or_add(
        self,
        lexeme:           str,
        atom_code:        int,
        line:             int,
        column:           int,
        len_before_trunc: int = 0,
        len_after_trunc:  int = 0,
    ) -> SymbolInfo:
        """
        Return the SymbolInfo for *lexeme*, creating it if this is the first
        occurrence.

        Parameters
        ----------
        lexeme           : uppercased, 30-char-truncated token string
        atom_code        : numeric atom code (e.g. 0xC01 for variable)
        line             : source line where this occurrence starts
        column           : source column (recorded only on first occurrence)
        len_before_trunc : total valid chars read before truncation
        len_after_trunc  : chars actually stored (≤ 30)
        """
        if lexeme in self._table:
            # Symbol already known — just record the new occurrence line
            symbol = self._table[lexeme]
            symbol.add_occurrence(line)
            return symbol

        # First time we see this lexeme — create the entry
        symbol = SymbolInfo(
            index            = self._next_index,
            lexeme           = lexeme,
            atom_code        = atom_code,
            len_before_trunc = len_before_trunc,
            len_after_trunc  = len_after_trunc,
        )
        symbol.add_occurrence(line)          # record first occurrence
        self._table[lexeme]  = symbol
        self._next_index    += 1
        return symbol

    def get(self, lexeme: str) -> SymbolInfo | None:
        """Return the SymbolInfo for *lexeme*, or None if not present."""
        return self._table.get(lexeme)

    def get_all_symbols(self) -> list[SymbolInfo]:
        """Return all symbols in insertion order (for the .TAB report)."""
        return list(self._table.values())