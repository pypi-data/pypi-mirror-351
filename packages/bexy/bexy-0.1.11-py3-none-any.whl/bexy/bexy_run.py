import sys
import os
import argparse
import re
from bexy.python_sandbox import PythonSandbox
from bexy.docker_sandbox import DockerSandbox

def extract_python_blocks_from_md(md_path):
    """Extract all Python code blocks from a Markdown file."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Match ```python ... ``` blocks
    pattern = re.compile(r'```python\s+([\s\S]*?)```', re.MULTILINE)
    return pattern.findall(content)

def run_code(code, use_docker=False):
    if use_docker:
        sandbox = DockerSandbox()
    else:
        sandbox = PythonSandbox()
    result = sandbox.run_code(code)
    print("\n=== Wynik wykonania kodu ===")
    print(f"Sukces: {result['success']}")
    print(f"Standardowe wyjście:\n{result['stdout']}")
    print(f"Standardowe wyjście błędów:\n{result['stderr']}")
    if 'required_packages' in result:
        print(f"Wymagane pakiety: {result['required_packages']}")
    if 'missing_packages' in result:
        print(f"Brakujące pakiety: {result['missing_packages']}")
    print("==========================\n")
    return result

def main():
    parser = argparse.ArgumentParser(description="Run Python code from .py or .md files using Bexy sandbox.")
    parser.add_argument('file', help="Path to .py or .md file")
    parser.add_argument('--docker', action='store_true', help="Run code in Docker sandbox")
    parser.add_argument('--auto', action='store_true', help="Automatically execute all Python code blocks in .md files without confirmation (default)")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Plik nie istnieje: {args.file}")
        sys.exit(1)

    ext = os.path.splitext(args.file)[1].lower()
    if ext == '.py':
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()
        print(f"\n>>> Uruchamianie pliku {args.file}...")
        run_code(code, use_docker=args.docker)
    elif ext == '.md':
        blocks = extract_python_blocks_from_md(args.file)
        if not blocks:
            print("Nie znaleziono bloków kodu Python w pliku Markdown.")
            sys.exit(1)
        print(f"Znaleziono {len(blocks)} bloków kodu Python w pliku {args.file}.")
        # Domyślnie automatycznie uruchamiaj wszystkie bloki
        for i, code in enumerate(blocks, 1):
            print(f"\n>>> Uruchamianie bloku #{i} z pliku {args.file}...")
            run_code(code, use_docker=args.docker)
    else:
        print("Obsługiwane są tylko pliki .py i .md")
        sys.exit(1)

if __name__ == "__main__":
    main()
