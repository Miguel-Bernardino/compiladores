class ReservedWords:
    def __init__(self):
        self._reserved_words_table = {
            "BOOLEAN"         :     0xA01, 
            "BREAK"           :     0xA02, 
            "CHARACTER"       :     0xA03,
            "DECLARATIONS"    :     0xA04, 
            "ELSE"            :     0xA05, 
            "ENDDECLARATIONS" :     0xA06,
            "ENDFUNCTION"     :     0xA07, 
            "ENDFUNCTIONS"    :     0xA08, 
            "ENDIF"           :     0xA09,
            "ENDPROGRAM"      :     0xA10, 
            "ENDWHILE"        :     0xA11, 
            "FALSE"           :     0xA12,
            "FUNCTIONS"       :     0xA13, 
            "FUNCTYPE"        :     0xA14, 
            "IF"              :     0xA15,
            "INTEGER"         :     0xA16, 
            "PARAMTYPE"       :     0xA17, 
            "PRINT"           :     0xA18,
            "PROGRAM"         :     0xA19, 
            "REAL"            :     0xA20, 
            "RETURN"          :     0xA21,
            "STRING"          :     0xA22, 
            "TRUE"            :     0xA23, 
            "VARTYPE"         :     0xA24,
            "VOID"            :     0xA25,
            "WHILE"           :     0xA26
        }

    # Method to check if a word belongs to the reserved words category.
    # if not found, it returns 0, otherwise it returns the corresponding code.
    def contains(self, word: str) -> int:
        """Checks if a word belongs to the category."""
        return self._reserved_words_table.get(str.upper(word), 0) 