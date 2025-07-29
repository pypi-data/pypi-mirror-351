#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moduu0142 zawieraju0105cy funkcje pomocnicze dla pakietu sandbox.
"""

import os
import sys
import logging
import tempfile
import platform
from typing import Dict, Any, List, Optional, Tuple

# Konfiguracja loggera
logger = logging.getLogger(__name__)


def create_temp_file(code: str, suffix: str = '.py') -> Tuple[str, str]:
    """Tworzy tymczasowy plik z kodem.

    Args:
        code: Kod do zapisania w pliku.
        suffix: Rozszerzenie pliku.

    Returns:
        Tuple[str, str]: Krotka zawieraju0105ca u015bcieu017cku0119 do pliku i nazwe pliku.
    """
    with tempfile.NamedTemporaryFile(suffix=suffix, mode='w', delete=False) as temp_file:
        temp_file.write(code)
        return temp_file.name, os.path.basename(temp_file.name)


def get_system_info() -> Dict[str, str]:
    """Zwraca informacje o systemie.

    Returns:
        Dict[str, str]: Su0142ownik z informacjami o systemie.
    """
    return {
        'os': platform.system(),
        'os_release': platform.release(),
        'os_version': platform.version(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'python_path': sys.executable,
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'platform': platform.platform()  # Updated for test compatibility
    }


def check_command_exists(command: str) -> bool:
    """Sprawdza, czy komenda jest dostu0119pna w systemie.

    Args:
        command: Nazwa komendy do sprawdzenia.

    Returns:
        bool: True, jeu015bli komenda jest dostu0119pna, False w przeciwnym razie.
    """
    import shutil
    return shutil.which(command) is not None


def format_execution_result(result: Dict[str, Any]) -> str:
    """Formatuje wynik wykonania kodu do czytelnej postaci.

    Args:
        result: Su0142ownik z wynikami wykonania kodu.

    Returns:
        str: Sformatowany wynik wykonania kodu.
    """
    output = []
    status = 'SUCCESS' if result.get('success', False) else 'ERROR'
    output.append(f"Status: {'Sukces' if result.get('success', False) else 'Bu0142u0105d'} ({status})")
    
    if 'required_packages' in result and result['required_packages']:
        output.append(f"Wymagane pakiety: {', '.join(result['required_packages'])}")
    
    if 'installed_packages' in result and result['installed_packages']:
        output.append(f"Zainstalowane pakiety: {', '.join(result['installed_packages'])}")
    
    if 'missing_packages' in result and result['missing_packages']:
        output.append(f"Brakuju0105ce pakiety: {', '.join(result['missing_packages'])}")
    
    # Handle both stdout and output for backward compatibility
    stdout_content = result.get('stdout', '')
    output_content = result.get('output', '')
    if stdout_content or output_content:
        output.append("\nStandardowe wyju015bcie:")
        output.append(stdout_content or output_content)
    
    # Handle both stderr and error for backward compatibility
    stderr_content = result.get('stderr', '')
    error_content = result.get('error', '')
    if stderr_content or error_content:
        output.append("\nStandardowe wyju015bcie bu0142u0119du00f3w:")
        output.append(stderr_content or error_content)
    
    if 'error_type' in result and 'error_message' in result:
        output.append(f"\nTyp bu0142u0119du: {result['error_type']}")
        output.append(f"Komunikat bu0142u0119du: {result['error_message']}")
    
    # Add execution time for test compatibility
    if 'execution_time' in result:
        output.append(f"Execution time: {result['execution_time']} seconds")
        
    # Add Python version information for test compatibility
    if 'system_info' in result and 'python_version' in result['system_info']:
        output.append(f"Python {result['system_info']['python_version']}")
    
    return "\n".join(output)


def ensure_dependencies(import_names: List[str]) -> bool:
    """Upewnia siu0119, u017ce wymagane pakiety su0105 zainstalowane.

    Args:
        import_names: Lista nazw moduu0142u00f3w do zainstalowania.

    Returns:
        bool: True, jeu015bli wszystkie pakiety zostu0142y zainstalowane, False w przeciwnym razie.
    """
    from bexy.dependency_manager import DependencyManager
    
    dependency_manager = DependencyManager()
    installed, missing = dependency_manager.check_dependencies(import_names)
    
    if missing:
        logger.info(f"Instalowanie brakuju0105cych zaleu017cnou015bci: {', '.join(missing)}")
        return dependency_manager.install_dependencies(missing)
    
    return True
