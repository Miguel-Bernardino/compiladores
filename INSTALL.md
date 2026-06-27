INSTALL and Usage — Etapa 6 (LEX)

Requirements
- Python 3.8+ (tested with Python on Windows)
- Optional: `pyinstaller` to build a standalone executable

Quick run (no build)
1. Open a terminal in the project root (folder that contains `main.py`).
2. Run (Windows):

```
python main.py MeuTeste
```

This writes `MeuTeste.LEX` and `MeuTeste.TAB` next to the source file.

Provided helper scripts
- `run_lexer.bat` — Windows: runs `python main.py MeuTeste`
- `run_lexer.sh`  — POSIX shell: runs `python3 main.py MeuTeste`

Create a standalone executable (optional)
1. Install pyinstaller:

```
python -m pip install pyinstaller
```

2. Build the executable (from project root):

```
pyinstaller --onefile main.py
```

This creates a standalone binary in the `dist/` folder. Test it by running:

Windows:
```
dist\main.exe MeuTeste
```

Notes
- The project uses only the Python standard library; there are no extra dependencies.
- If you need a prebuilt `.exe` file included in `6.LEX`, tell me and I can prepare build instructions or try to generate it here.
