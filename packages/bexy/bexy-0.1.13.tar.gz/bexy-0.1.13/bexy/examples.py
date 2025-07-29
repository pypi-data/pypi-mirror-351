#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Przykłady użycia pakietu sandbox.

Ten moduł zawiera przykłady użycia różnych komponentów pakietu sandbox.
"""

import os
import sys
import logging
import questionary
from bexy.bexy_run import extract_python_blocks_from_md, run_code

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Przykładowe kody Python do testów
EXAMPLE_CODE_SIMPLE = """
import os
import sys
import math

print('Informacje o systemie:')
print(f'System operacyjny: {os.name}')
print(f'Wersja Pythona: {sys.version}')
print(f'Katalog bieżący: {os.getcwd()}')

# Przykład obliczeń matematycznych
print('\nObliczenia matematyczne:')
print(f'Pi: {math.pi}')
print(f'Pierwiastek z 16: {math.sqrt(16)}')
print(f'Silnia z 5: {math.factorial(5)}')
"""

EXAMPLE_CODE_NUMPY = """
import numpy as np
import matplotlib.pyplot as plt

# Przykład użycia NumPy
arr = np.array([1, 2, 3, 4, 5])
print(f'Tablica NumPy: {arr}')
print(f'Średnia: {np.mean(arr)}')
print(f'Suma: {np.sum(arr)}')
print(f'Odchylenie standardowe: {np.std(arr)}')

# Przykład generowania wykresu
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.figure(figsize=(8, 4))
plt.plot(x, y)
plt.title('Funkcja sinus')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.grid(True)
plt.savefig('sinus.png')
print('Wykres zapisany do pliku sinus.png')
"""

EXAMPLE_CODE_ERROR = """
print('Ten kod zawiera błąd składni')
if True
    print('Brakuje dwukropka po if')
"""

EXAMPLE_CODE_RUNTIME_ERROR = """
print('Ten kod zawiera błąd wykonania')
x = 10 / 0  # Dzielenie przez zero
print('Ta linia nie zostanie wykonana')
"""

EXAMPLE_CODE_FILE_OPERATIONS = """
import os
import tempfile

# Utworzenie tymczasowego pliku
temp_file = tempfile.NamedTemporaryFile(delete=False)
temp_path = temp_file.name
temp_file.close()

# Zapisanie danych do pliku
with open(temp_path, 'w') as f:
    f.write('Hello, world!\n')
    f.write('To jest przykład operacji na plikach.')

# Odczytanie danych z pliku
print(f'Odczytywanie pliku: {temp_path}')
with open(temp_path, 'r') as f:
    content = f.read()
    print(content)

# Usunięcie pliku
os.unlink(temp_path)
print(f'Plik {temp_path} został usunięty.')
"""


def example_code_analyzer():
    """Przykład użycia CodeAnalyzer."""
    from bexy.code_analyzer import CodeAnalyzer
    
    analyzer = CodeAnalyzer()
    
    print("\n=== Przykład użycia CodeAnalyzer ===\n")
    
    # Analiza kodu z importami standardowymi
    print("Analiza kodu z importami standardowymi:")
    result = analyzer.analyze_code(EXAMPLE_CODE_SIMPLE)
    print(f"Standardowe biblioteki: {result['standard_library']}")
    print(f"Zewnętrzne biblioteki: {result['third_party']}")
    print(f"Nieznane biblioteki: {result['unknown']}")
    print(f"Wymagane pakiety: {result['required_packages']}")
    
    # Analiza kodu z importami zewnętrznymi
    print("\nAnaliza kodu z importami zewnętrznymi:")
    result = analyzer.analyze_code(EXAMPLE_CODE_NUMPY)
    print(f"Standardowe biblioteki: {result['standard_library']}")
    print(f"Zewnętrzne biblioteki: {result['third_party']}")
    print(f"Nieznane biblioteki: {result['unknown']}")
    print(f"Wymagane pakiety: {result['required_packages']}")
    
    # Analiza kodu z błędem składni
    print("\nAnaliza kodu z błędem składni:")
    result = analyzer.analyze_code(EXAMPLE_CODE_ERROR)
    print(f"Wynik: {result}")


def example_dependency_manager():
    """Przykład użycia DependencyManager."""
    from bexy.dependency_manager import DependencyManager
    
    dependency_manager = DependencyManager()
    
    print("\n=== Przykład użycia DependencyManager ===\n")
    
    # Sprawdzenie zainstalowanych pakietów
    print("Sprawdzenie zainstalowanych pakietów:")
    packages = ['os', 'sys', 'math', 'numpy', 'pandas', 'nonexistent_package']
    for package in packages:
        installed = dependency_manager.check_package_installed(package)
        print(f"Pakiet {package}: {'zainstalowany' if installed else 'niezainstalowany'}")
    
    # Analiza zależności
    print("\nAnaliza zależności:")
    result = dependency_manager.analyze_dependencies(EXAMPLE_CODE_NUMPY)
    print(f"Wymagane pakiety: {result['required_packages']}")
    print(f"Zainstalowane pakiety: {result['installed_packages']}")
    print(f"Brakujące pakiety: {result['missing_packages']}")


def example_python_sandbox():
    """Przykład użycia PythonSandbox."""
    from bexy.python_sandbox import PythonSandbox
    
    sandbox = PythonSandbox()
    
    print("\n=== Przykład użycia PythonSandbox ===\n")
    
    # Uruchomienie prostego kodu
    print("Uruchomienie prostego kodu:")
    result = sandbox.run_code(EXAMPLE_CODE_SIMPLE)
    print(f"Sukces: {result['success']}")
    print(f"Standardowe wyjście:\n{result['stdout']}")
    
    # Uruchomienie kodu z błędem składni
    print("\nUruchomienie kodu z błędem składni:")
    result = sandbox.run_code(EXAMPLE_CODE_ERROR)
    print(f"Sukces: {result['success']}")
    print(f"Standardowe wyjście błędów:\n{result['stderr']}")
    
    # Uruchomienie kodu z błędem wykonania
    print("\nUruchomienie kodu z błędem wykonania:")
    result = sandbox.run_code(EXAMPLE_CODE_RUNTIME_ERROR)
    print(f"Sukces: {result['success']}")
    print(f"Standardowe wyjście:\n{result['stdout']}")
    print(f"Standardowe wyjście błędów:\n{result['stderr']}")


def example_docker_sandbox():
    """Przykład użycia DockerSandbox."""
    from bexy.docker_sandbox import DockerSandbox
    
    # Sprawdzenie, czy Docker jest zainstalowany
    import subprocess
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        docker_installed = result.returncode == 0
    except Exception:
        docker_installed = False
    
    if not docker_installed:
        print("\n=== Przykład użycia DockerSandbox ===\n")
        print("Docker nie jest zainstalowany. Pomijanie przykładu.")
        return
    
    sandbox = DockerSandbox()
    
    print("\n=== Przykład użycia DockerSandbox ===\n")
    
    # Uruchomienie prostego kodu w Dockerze
    print("Uruchomienie prostego kodu w Dockerze:")
    result = sandbox.run_code(EXAMPLE_CODE_SIMPLE)
    print(f"Sukces: {result['success']}")
    print(f"Standardowe wyjście:\n{result['stdout']}")


def example_sandbox_manager():
    """Przykład użycia SandboxManager."""
    from bexy.sandbox_manager import SandboxManager
    
    # Utworzenie SandboxManager
    manager = SandboxManager(use_docker=False)
    
    print("\n=== Przykład użycia SandboxManager ===\n")
    
    # Uruchomienie kodu lokalnie
    print("Uruchomienie kodu lokalnie:")
    result = manager.run_code(EXAMPLE_CODE_SIMPLE)
    print(manager.format_result(result))
    
    # Sprawdzenie, czy Docker jest zainstalowany
    import subprocess
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        docker_installed = result.returncode == 0
    except Exception:
        docker_installed = False
    
    if docker_installed:
        # Utworzenie SandboxManager z Dockerem
        docker_manager = SandboxManager(use_docker=True)
        
        # Uruchomienie kodu w Dockerze
        print("\nUruchomienie kodu w Dockerze:")
        result = docker_manager.run_code(EXAMPLE_CODE_SIMPLE)
        print(docker_manager.format_result(result))


def example_utils():
    """Przykład użycia funkcji pomocniczych."""
    from bexy.utils import get_system_info, format_execution_result, create_temp_file
    
    print("\n=== Przykład użycia funkcji pomocniczych ===\n")
    
    # Informacje o systemie
    print("Informacje o systemie:")
    system_info = get_system_info()
    for key, value in system_info.items():
        print(f"{key}: {value}")
    
    # Utworzenie tymczasowego pliku
    print("\nUtworzenie tymczasowego pliku:")
    file_path, file_name = create_temp_file("print('Hello, world!')")
    print(f"Utworzono plik: {file_path}")
    
    # Formatowanie wyniku wykonania kodu
    print("\nFormatowanie wyniku wykonania kodu:")
    result = {
        'success': True,
        'stdout': 'Hello, world!',
        'stderr': '',
        'required_packages': ['numpy', 'pandas'],
        'installed_packages': ['numpy'],
        'missing_packages': ['pandas']
    }
    formatted = format_execution_result(result)
    print(formatted)
    
    # Usunięcie tymczasowego pliku
    try:
        os.unlink(file_path)
        print(f"Usunięto plik: {file_path}")
    except Exception as e:
        print(f"Błąd podczas usuwania pliku: {e}")


def main():
    """Główna funkcja uruchamiająca przykłady z interaktywnym menu."""
    menu_choices = [
        "Przykład: CodeAnalyzer",
        "Przykład: DependencyManager",
        "Przykład: PythonSandbox",
        "Przykład: DockerSandbox",
        "Przykład: SandboxManager",
        "Przykład: Utils",
        "Uruchom kod z pliku .py lub .md",
        "Wyjście"
    ]
    while True:
        print("\n=== Przykłady użycia pakietu sandbox ===")
        choice = questionary.select(
            "Wybierz przykład do uruchomienia:",
            choices=menu_choices
        ).ask()
        if choice == "Przykład: CodeAnalyzer":
            example_code_analyzer()
        elif choice == "Przykład: DependencyManager":
            example_dependency_manager()
        elif choice == "Przykład: PythonSandbox":
            example_python_sandbox()
        elif choice == "Przykład: DockerSandbox":
            example_docker_sandbox()
        elif choice == "Przykład: SandboxManager":
            example_sandbox_manager()
        elif choice == "Przykład: Utils":
            example_utils()
        elif choice == "Uruchom kod z pliku .py lub .md":
            file_path = questionary.text("Podaj ścieżkę do pliku .py lub .md:").ask()
            use_docker = questionary.confirm("Uruchomić w Dockerze?", default=False).ask()
            if not file_path:
                print("Nie podano ścieżki do pliku.")
                continue
            import os
            ext = os.path.splitext(file_path)[1].lower()
            if not os.path.isfile(file_path):
                print(f"Plik nie istnieje: {file_path}")
                continue
            if ext == '.py':
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                print(f"\n>>> Uruchamianie pliku {file_path}...")
                run_code(code, use_docker=use_docker)
            elif ext == '.md':
                blocks = extract_python_blocks_from_md(file_path)
                if not blocks:
                    print("Nie znaleziono bloków kodu Python w pliku Markdown.")
                    continue
                print(f"Znaleziono {len(blocks)} bloków kodu Python w pliku {file_path}.")
                for i, code in enumerate(blocks, 1):
                    print(f"\n>>> Uruchamianie bloku #{i} z pliku {file_path}...")
                    run_code(code, use_docker=use_docker)
            else:
                print("Obsługiwane są tylko pliki .py i .md")
        elif choice == "Wyjście":
            print("Do widzenia!")
            break


if __name__ == "__main__":
    main()
