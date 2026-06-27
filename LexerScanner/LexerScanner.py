from Reserved.ReservedSymbols import ReservedSymbols
from Reserved.ReservedWords import ReservedWords
from Reserved.ReservedIdentifiers import ReservedIdentifiers
from Token.Token import Token
from Token.TokenType import TokenType
from Symbol.SymbolTable import SymbolTable

# ---------------------------------------------------------------------------
# Characters that are valid anywhere in the language source.
# Anything NOT in this set is an invalid character → level-1 silent filter.
# ---------------------------------------------------------------------------
_VALID_CHARS = set(
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '0123456789'
    '_ "\''                      # underscore, double-quote, single-quote
    ';,:.?()[]{}+-*/%<>=!#'      # operators / punctuation
    ' \t\r\n'                    # whitespace (delimiters, not atoms)
)

MAX_ATOM_LEN = 30   # spec: max 30 valid chars per atom

# ---------------------------------------------------------------------------
# Level-2 filter: repair truncated atoms (max 30 chars) so they remain valid.
# Examples: ensure `123.` becomes `123` or `1.23` is kept; force-close strings
# that lost their ending quote at the 30-char limit.
# ---------------------------------------------------------------------------

def _level2_repair_realconst(chars: list[str]) -> list[str]:
    """Repair a truncated real constant (max 30 chars).

    Return a list matching <digits>.<digits>, or [] if it cannot be fixed.
    """
    s = ''.join(chars)

    dot_pos = s.find('.')
    if dot_pos == -1:
        return []   # truncation removed the dot -> not a realConst

    int_part = s[:dot_pos]
    if not int_part or not int_part.isdigit():
        return []

    # collect only contiguous fractional digits after the point
    frac_digits = ''
    for c in s[dot_pos + 1:]:
        if c.isdigit():
            frac_digits += c
        else:
            break
    if not frac_digits:
        return []
    return list(int_part + '.' + frac_digits)


def _level2_repair_string(chars: list[str]) -> list[str]:
    """Ensure a truncated string ends with a closing quote.

    If the closing quote is missing at the 30-char limit, replace the last
    character with a quote to force termination.
    """
    if not chars:
        return chars
    if chars[-1] == '"':
        return chars
    repaired = chars[:]
    repaired[-1] = '"'
    return repaired


# Characters valid inside a stringConst body
_MIOLO_CHARS = set(
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '0123456789 $_.'
)


class LexerScanner:
    def __init__(self, source_code: str):
        self.source_code      = source_code
        self.position         = 0
        self.line             = 1
        self.column           = 1
        self.symbol_table     = SymbolTable()
        self.reserved_words   = ReservedWords()
        self.reserved_symbols = ReservedSymbols()
        self.reserved_ids     = ReservedIdentifiers()

    # ------------------------------------------------------------------
    # Low-level navigation helpers
    # ------------------------------------------------------------------

    def _current(self) -> str | None:
        """Current character without advancing, or None at EOF."""
        return self.source_code[self.position] if self.position < len(self.source_code) else None

    def _peek(self, offset: int = 1) -> str | None:
        """Look ahead without advancing."""
        idx = self.position + offset
        return self.source_code[idx] if idx < len(self.source_code) else None

    def advance(self):
        """Advance one character, keeping line/column in sync."""
        if self.position < len(self.source_code):
            if self.source_code[self.position] == '\n':
                self.line  += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

    def _is_valid(self, ch: str) -> bool:
        return ch in _VALID_CHARS

    # ------------------------------------------------------------------
    # Whitespace & comment skipping
    # ------------------------------------------------------------------

    def skip_whitespace(self):
        while self.position < len(self.source_code) and self.source_code[self.position] in ' \t\r\n':
            self.advance()

    def _skip_line_comment(self):
        """Consume from current position to end-of-line (or EOF)."""
        while self.position < len(self.source_code) and self.source_code[self.position] != '\n':
            self.advance()

    def _skip_block_comment(self):
        """Consume until '*/' or EOF (spec: rest-of-file is comment if unclosed)."""
        while self.position < len(self.source_code):
            if self.source_code[self.position] == '*' and self._peek() == '/':
                self.advance()  # '*'
                self.advance()  # '/'
                return
            self.advance()

    def _skip_whitespace_and_comments(self):
        """
        Repeatedly eat whitespace and both comment flavours until we reach
        the start of a real atom or EOF.
        """
        while True:
            self.skip_whitespace()
            ch = self._current()
            if ch is None:
                break
            if ch == '/' and self._peek() == '/':
                self.advance(); self.advance()   # consume '//'
                self._skip_line_comment()
            elif ch == '/' and self._peek() == '*':
                self.advance(); self.advance()   # consume '/*'
                self._skip_block_comment()
            else:
                break

    # ------------------------------------------------------------------
    # Identifiers, reserved words, and variables
    # ------------------------------------------------------------------

    def recognize_identifier_or_keyword(self) -> Token | None:
        """
        Reads a sequence of (letter | digit | underscore) chars.

        Spec patterns (Appendix C):
          programName  / functionName  ::= letter (letter | digit)*
          variable                     ::= (letter | '_') (letter | digit | '_')*

        At the lexical level both look the same (the parser disambiguates
        context), so every non-reserved sequence is treated as VARIABLE (C01).

                Behavior summary:
                    - Read letters/digits/'_' up to 30 chars, then uppercase for storage.
                    - Ignore invalid chars silently while building the atom.
                    - If the resulting lexeme is a reserved word, return RESERVED_WORD.
                    - Otherwise store as RESERVED_IDENTIFIER in the symbol table.
        """
        start_line   = self.line
        start_column = self.column

        raw_chars: list[str] = []   # every valid char consumed (no limit)
        stored_count = 0            # how many chars we actually store (≤ 30)

        while self.position < len(self.source_code):
            ch = self.source_code[self.position]
            if ch.isalnum() or ch == '_':
                raw_chars.append(ch)
                stored_count += 1
                self.advance()
            elif self._is_valid(ch):
                break               # delimiter → stop
            else:
                self.advance()      # invalid char → discard silently, keep going

        raw_lexeme  = ''.join(raw_chars)
        len_before  = len(raw_lexeme)                    # chars before truncation
        truncated   = raw_lexeme[:MAX_ATOM_LEN].upper()  # 30-char cap + uppercase
        len_after   = len(truncated)                     # chars after truncation

        # 1. Reserved word? (A-codes)
        code = self.reserved_words.contains(truncated)
        if code:
            return Token(TokenType.RESERVED_WORD, truncated, start_line, start_column)

        # 2. Plain identifier → C01, goes into symbol table
        id_code = self.reserved_ids.contains("VARIABLE")  # 0xC01
        self.symbol_table.get_or_add(
            truncated, id_code, start_line, start_column,
            len_before_trunc=len_before, len_after_trunc=len_after
        )
        return Token(TokenType.RESERVED_IDENTIFIER, truncated, start_line, start_column)

    # ------------------------------------------------------------------
    # Integer and real constants
    # ------------------------------------------------------------------

    def _recognize_number(self) -> Token | None:
        """
        intConst  ::= digit+
        realConst ::= digit+ '.' digit+

        Both are identifiers (C06 / C07) stored in the symbol table.
        30-char limit applies; invalid chars are silently filtered.
        Returns TokenType.RESERVED_IDENTIFIER in both cases.
        """
        start_line   = self.line
        start_column = self.column

        chars: list[str] = []
        total_valid = 0   # all valid chars seen (for len_before_trunc)

        def _store(c: str):
            """Append c only while under the 30-char cap."""
            if len(chars) < MAX_ATOM_LEN:
                chars.append(c)

        # --- integer part ---
        while self.position < len(self.source_code):
            ch = self.source_code[self.position]
            if ch.isdigit():
                _store(ch)
                total_valid += 1
                self.advance()
            elif self._is_valid(ch):
                break
            else:
                self.advance()  # level-1 filter

        is_real = False

        # --- optional fractional part: '.' digit+ ---
        if self._current() == '.' and self._peek() is not None and (self._peek() or '').isdigit():
            is_real = True
            _store('.')
            total_valid += 1
            self.advance()  # consume '.'

            while self.position < len(self.source_code):
                ch = self.source_code[self.position]
                if ch.isdigit():
                    _store(ch)
                    total_valid += 1
                    self.advance()
                elif self._is_valid(ch):
                    break
                else:
                    self.advance()

        lexeme  = ''.join(chars)
        id_key  = "REALCONST" if is_real else "INTCONST"

        # ------------------------------------------------------------------
        # Level-2 filter — realConst
        # After truncation at the 30-char limit the lexeme may be incoherent
        # (for example it may end with '.' or lack fractional digits).
        # _level2_repair_realconst repairs the lexeme; if it returns [] the
        # atom is invalid and is silently discarded.
        # ------------------------------------------------------------------
        if is_real:
            repaired = _level2_repair_realconst(chars)
            if not repaired:
                # atom could not be repaired — discard (level 2)
                return None
            lexeme = ''.join(repaired)

        id_code = self.reserved_ids.contains(id_key)
        self.symbol_table.get_or_add(
            lexeme, id_code, start_line, start_column,
            len_before_trunc=total_valid, len_after_trunc=len(lexeme)
        )
        return Token(TokenType.RESERVED_IDENTIFIER, lexeme, start_line, start_column)

    # ------------------------------------------------------------------
    # String constants
    # ------------------------------------------------------------------

    def _recognize_string_const(self) -> Token | None:
        """
        stringConst ::= '"' miolo '"'
        miolo = (letter | digit | blank | '$' | '_' | '.')*

        Opening and closing quotes count toward the 30-char limit.
        Invalid chars inside the miolo are silently filtered.
        """
        start_line   = self.line
        start_column = self.column

        chars: list[str] = ['"']
        total_valid = 1          # opening quote
        self.advance()           # consume '"'

        while self.position < len(self.source_code):
            ch = self.source_code[self.position]
            if ch == '"':
                # closing quote — store if still under cap
                if len(chars) < MAX_ATOM_LEN:
                    chars.append('"')
                total_valid += 1
                self.advance()
                break
            elif ch in _MIOLO_CHARS:
                if len(chars) < MAX_ATOM_LEN:
                    chars.append(ch)
                total_valid += 1
                self.advance()
            else:
                self.advance()   # invalid inside string → filter

        # ------------------------------------------------------------------
        # Level-2 fix for strings
        # If the string reached the 30-char limit without a closing quote,
        # _level2_repair_string will force a closing quote at position 30.
        # Unclosed strings at EOF are also handled by the same repair.
        # ------------------------------------------------------------------
        chars   = _level2_repair_string(chars)
        lexeme  = ''.join(chars).upper()
        id_code = self.reserved_ids.contains("STRINGCONST")
        self.symbol_table.get_or_add(
            lexeme, id_code, start_line, start_column,
            len_before_trunc=total_valid, len_after_trunc=len(lexeme)
        )
        return Token(TokenType.RESERVED_IDENTIFIER, lexeme, start_line, start_column)

    # ------------------------------------------------------------------
    # Character constants
    # ------------------------------------------------------------------

    def _recognize_char_const(self) -> Token | None:
        """
        charConst ::= "'" letter "'"   (exactly 3 chars, quotes included)
        Returns TokenType.RESERVED_IDENTIFIER (C05).
        If the literal is malformed the opening quote is discarded and None
        is returned so the scanner keeps going.
        """
        start_line   = self.line
        start_column = self.column
        self.advance()   # consume opening "'"

        ch = self._current()
        if ch is not None and ch.isalpha():
            letter = ch.upper()
            self.advance()
            if self._current() == "'":
                self.advance()   # consume closing "'"
                lexeme  = f"'{letter}'"
                id_code = self.reserved_ids.contains("CHARCONST")
                self.symbol_table.get_or_add(
                    lexeme, id_code, start_line, start_column,
                    len_before_trunc=3, len_after_trunc=3
                )
                return Token(TokenType.RESERVED_IDENTIFIER, lexeme, start_line, start_column)

        # Malformed — opening quote already consumed, just continue
        return None

    # ------------------------------------------------------------------
    # Reserved symbols (operators / punctuation)
    # ------------------------------------------------------------------

    def _recognize_symbol(self) -> Token | None:
        """
        Maximal-munch: try 2-char symbol first, then 1-char.
        Reserved symbols are NOT stored in the symbol table.
        Returns TokenType.RESERVED_SYMBOL.
        """
        start_line   = self.line
        start_column = self.column

        # Two-character candidates
        if self._peek() is not None:
            two  = self.source_code[self.position:self.position + 2]
            code = self.reserved_symbols.contains(two)
            if code:
                self.advance(); self.advance()
                return Token(TokenType.RESERVED_SYMBOL, two, start_line, start_column)

        # Single-character candidates
        one  = self.source_code[self.position]
        code = self.reserved_symbols.contains(one)
        if code:
            self.advance()
            return Token(TokenType.RESERVED_SYMBOL, one, start_line, start_column)

        return None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_next_token(self) -> Token | None:
        """Return the next Token or None at EOF.

        Dispatch order after skipping whitespace/comments:
            1. letter / '_'   -> identifier or reserved word
            2. digit          -> intConst or realConst
            3. '"'            -> stringConst
            4. "'"            -> charConst
            5. operator/punct  -> reserved symbol
            6. invalid char    -> silently skip and continue

        If a sub-recognizer returns None (atom discarded by level-2 repair),
        the loop continues looking for the next atom instead of returning EOF.
        """
        while True:
            self._skip_whitespace_and_comments()

            if self.position >= len(self.source_code):
                return None

            ch = self.source_code[self.position]

            if ch.isalpha() or ch == '_':
                return self.recognize_identifier_or_keyword()

            if ch.isdigit():
                tok = self._recognize_number()
                if tok is not None:
                    return tok
                continue   # realConst discarded by level-2 repair — continue to next atom

            if ch == '"':
                return self._recognize_string_const()

            if ch == "'":
                tok = self._recognize_char_const()
                if tok is not None:
                    return tok
                continue   # malformed charConst — continue to next atom

            tok = self._recognize_symbol()
            if tok is not None:
                return tok

            # Invalid character — silently skip (level-1 filter)
            self.advance()