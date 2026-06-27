from dataclasses import dataclass, field

MAX_LINES_STORED = 5   # spec: store only the first 5 occurrences


@dataclass
class SymbolInfo:
    """
    Stores every attribute the .TAB report requires for a single symbol.

    Fields set at creation time (never change after the symbol is first seen):
        index            - position in the symbol table (1-based)
        lexeme           - uppercased, truncated to 30 chars
        atom_code        - numeric code from the Reserved tables (e.g. 0xC01)
        len_before_trunc - total valid chars read before the 30-char cut
        len_after_trunc  - chars actually stored (≤ 30)

    Fields that may be updated during analysis:
        symbol_type - semantic type filled in by the parser ('FP','IN','ST',
                      'CH','BL','VD','AF','AI','AS','AC','AB'), '-' until set
        lines       - list of the first 5 source lines where the symbol appears
    """

    index:            int
    lexeme:           str
    atom_code:        int
    len_before_trunc: int
    len_after_trunc:  int
    symbol_type:      str       = '-'
    lines:            list[int] = field(default_factory=list)

    def add_occurrence(self, line: int):
        """Record a new occurrence line (only the first MAX_LINES_STORED are kept)."""
        if len(self.lines) < MAX_LINES_STORED:
            self.lines.append(line)

    def formatted_lines(self) -> str:
        """Return lines formatted as the spec example: (1, 2, 2, 2, 3)"""
        return '(' + ', '.join(str(ln) for ln in self.lines) + ')'