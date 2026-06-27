class ReservedIdentifiers:
    def __init__(self):
        self._reserved_identifiers_table = {
            "VARIABLE"         :     0xC01, 
            "FUNCTIONNAME"     :     0xC02,
            "PROGRAMNAME"      :     0xC03,
            "STRINGCONST"      :     0xC04,
            "CHARCONST"        :     0xC05,
            "INTCONST"         :     0xC06,
            "REALCONST"        :     0xC07
        }

    # Method to check if a word belongs to the reserved words category.
    # if not found, it returns 0, otherwise it returns the corresponding code.
    def contains(self, word: str) -> int:
        """Checks if a word belongs to the category."""
        return self._reserved_identifiers_table.get(str.upper(word), 0) 