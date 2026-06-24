class ReservedSymbols:
    def __init__(self):
        self._reserved_symbol_table = {
            ";"         :  {  0xB01, "semicolon"            }, 
            ","         :  {  0xB02, "comma"                }, 
            ":"         :  {  0xB03, "colon"                }, 
            ":="        :  {  0xB04, "assignment"           },
            "?"         :  {  0xB05, "questionMark"         }, 
            "("         :  {  0xB06, "leftParenthesis"      }, 
            ")"         :  {  0xB07, "rightParenthesis"     }, 
            "["         :  {  0xB08, "leftBracket"          },
            "]"         :  {  0xB09, "rightBracket"         }, 
            "{"         :  {  0xB10, "leftBrace"            },
            "}"         :  {  0xB11, "rightBrace"           }, 
            "+"         :  {  0xB12, "plus"                 },
            "-"         :  {  0xB13, "minus"                }, 
            "*"         :  {  0xB14, "multiplication"       }, 
            "/"         :  {  0xB15, "division"             }, 
            "%"         :  {  0xB16, "modulo"               },
            "=="        :  {  0xB17, "equalComparison"      }, 
            "!="        :  {  0xB18, "notEqual"             }, 
            "#"         :  {  0xB18, "hash (alias for !=)"  }, 
            "<"         :  {  0xB19, "lessThan"             },
            "<="        :  {  0xB20, "lessEqual"            }, 
            ">"         :  {  0xB21, "greaterThan"          },
            ">="        :  {  0xB22, "greaterEqual"         }
        }

    # Method to check if a word belongs to the reserved symbols category.
    # if not found, it returns 0, otherwise it returns the corresponding code.
    def contains(self, word: str) -> int:
        """Checks if a word belongs to the category."""
        return self._reserved_symbol_table.get(str.upper(word), 0)[0]
    
    def get_description(self, word: str) -> str:
        """Returns the description of the reserved symbol."""
        return self._reserved_symbol_table.get(str.upper(word), [0, "Unknown"])[1] 