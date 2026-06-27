import sys
import os
from LexerScanner.LexerScanner import LexerScanner
from Token.TokenType import TokenType

# ---------------------------------------------------------------------------
# Team information — fill in your team's data here
# ---------------------------------------------------------------------------
TEAM_CODE  = "E02"
COMPONENTS = [
    ("Miguel Bernardino Sousa Borges da Silva",   "miguel.silva@aln.senaicimatec.edu.br",   "(71)99956-7589"),
    ("Felipe Costa Lino Almeida", "f.almeida@aln.senaicimatec.edu.br", "(71)99986-4321"),
    ("Guilherme Soares May Rios",  "guilherme.rios@aln.senaicimatec.edu.br",  "(71)99958-9990"),
    ("Daniel Fernandes da Cunha Vasconcelos",  "daniel.vasconcelos@aln.senaicimatec.edu.br",  "(71)99934-0512")
]


# ---------------------------------------------------------------------------
# Helper: convert numeric atom code to formatted string (A01, B04, C01, ...)
# ---------------------------------------------------------------------------
def format_atom_code(token_type: TokenType, atom_code: int) -> str:
    """
    Converts a numeric code like 0xA15 → 'A15', 0xB04 → 'B04', 0xC01 → 'C01'.
    The prefix letter comes from the TokenType enum value ('A', 'B', 'C').
    The numeric suffix is the lower byte of the code, zero-padded to 2 digits.
    """
    prefix = token_type.value                  # 'A', 'B', or 'C'
    number = atom_code & 0xFF                  # lower byte  e.g. 0xA15 → 0x15 → 21
    return f"{prefix}{number:02d}"


# ---------------------------------------------------------------------------
# Report header (shared by both .LEX and .TAB)
# ---------------------------------------------------------------------------
def build_header(title: str, source_filename: str) -> str:
    lines = [f"Código da Equipe: {TEAM_CODE}", "Componentes:"]
    for name, email, phone in COMPONENTS:
        lines.append(f"{name}; {email}; {phone}")
    lines.append("")
    lines.append(f"{title}")
    lines.append(f"Texto fonte analisado: {source_filename}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# .LEX report
# ---------------------------------------------------------------------------
def generate_lex_report(lex_entries: list, source_filename: str) -> str:
    """
    lex_entries: list of tuples
        (token, atom_code, symbol_table_index)
        where symbol_table_index is an int for identifiers or None for
        reserved words / symbols.
    """
    lines = [build_header("RELATÓRIO DA ANÁLISE LÉXICA.", source_filename)]

    for token, atom_code, sym_index in lex_entries:
        code_str  = format_atom_code(token.type, atom_code)
        index_str = str(sym_index) if sym_index is not None else "-"
        lines.append(
            f"Lexeme: {token.lexeme}, "
            f"Código: {code_str}, "
            f"indiceTabSimb: {index_str}, "
            f"Linha: {token.line}."
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# .TAB report
# ---------------------------------------------------------------------------
def generate_tab_report(symbol_table, source_filename: str) -> str:
    lines = [build_header("RELATÓRIO DA TABELA DE SÍMBOLOS.", source_filename)]

    for symbol in symbol_table.get_all_symbols():
        # Derive the formatted code string from the atom_code stored in SymbolInfo
        # The prefix letter matches the token type: C-codes are RESERVED_IDENTIFIER
        code_str = f"C{symbol.atom_code & 0xFF:02d}"

        lines.append(
            f"Entrada: {symbol.index}, "
            f"Código: {code_str}, "
            f"Lexeme: {symbol.lexeme},"
        )
        lines.append(
            f"QtdCharsAntesTrunc: {symbol.len_before_trunc}, "
            f"QtdCharDepoisTrunc: {symbol.len_after_trunc},"
        )
        lines.append(
            f"TipoSimb: {symbol.symbol_type}, "
            f"Linhas: {symbol.formatted_lines()}."
        )
        lines.append("-" * 64)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Lexer driver — runs the scanner and collects all tokens + metadata
# ---------------------------------------------------------------------------
def run_lexer(source_code: str):
    """
    Runs the LexerScanner over *source_code* and returns:
      - lex_entries : list of (Token, atom_code, symbol_table_index | None)
      - symbol_table: the populated SymbolTable instance
    """
    scanner     = LexerScanner(source_code)
    lex_entries = []

    while True:
        token = scanner.get_next_token()
        if token is None:
            break

        lexeme = token.lexeme

        if token.type == TokenType.RESERVED_WORD:
            # Look up the numeric code from the reserved-words table
            atom_code = scanner.reserved_words.contains(lexeme)
            lex_entries.append((token, atom_code, None))

        elif token.type == TokenType.RESERVED_SYMBOL:
            # Look up the numeric code from the reserved-symbols table
            atom_code = scanner.reserved_symbols.contains(lexeme)
            lex_entries.append((token, atom_code, None))

        elif token.type == TokenType.RESERVED_IDENTIFIER:
            # The symbol was already added to the table by the scanner;
            # retrieve it to get its index and atom_code.
            symbol    = scanner.symbol_table.get(lexeme)
            atom_code = symbol.atom_code if symbol else 0
            sym_index = symbol.index     if symbol else "-"
            lex_entries.append((token, atom_code, sym_index))

    return lex_entries, scanner.symbol_table


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <nome_do_arquivo>")
        print("Exemplo: python main.py MeuTeste")
        sys.exit(1)

    input_arg = sys.argv[1]

    # Resolve path: if only a name was given, look in the current directory;
    # if a full path was given, use it as-is.
    if os.path.dirname(input_arg):
        base_path = input_arg          # full path provided
    else:
        base_path = os.path.join(os.getcwd(), input_arg)

    source_path = base_path + ".261"
    lex_path    = base_path + ".LEX"
    tab_path    = base_path + ".TAB"
    source_filename = os.path.basename(source_path)

    # Open source file
    if not os.path.exists(source_path):
        print(f"Erro: arquivo '{source_path}' não encontrado.")
        sys.exit(1)

    with open(source_path, "r", encoding="ascii", errors="replace") as f:
        source_code = f.read()

    # Run lexer
    lex_entries, symbol_table = run_lexer(source_code)

    # Generate and write .LEX
    lex_report = generate_lex_report(lex_entries, source_filename)
    with open(lex_path, "w", encoding="utf-8") as f:
        f.write(lex_report)

    # Generate and write .TAB
    tab_report = generate_tab_report(symbol_table, source_filename)
    with open(tab_path, "w", encoding="utf-8") as f:
        f.write(tab_report)

    print(f"Análise concluída.")
    print(f"  Relatório léxico  : {lex_path}")
    print(f"  Tabela de símbolos: {tab_path}")


if __name__ == "__main__":
    main()