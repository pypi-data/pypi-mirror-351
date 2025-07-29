#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for managing different types of sandboxes.
"""

import os
import logging
from typing import Dict, Any, Optional, Union

from .python_sandbox import PythonSandbox
from .docker_sandbox import DockerSandbox
from .utils import get_system_info, format_execution_result

# Logger configuration
logger = logging.getLogger(__name__)


class SandboxManager:
    """Class for managing different types of sandboxes."""

    def __init__(self, use_docker: bool = False, docker_image: Optional[str] = None):
        """Initializes the sandbox manager.

        Args:
            use_docker: Whether to use Docker for running code.
            docker_image: Docker image name to use (optional).
        """
        self.use_docker = use_docker
        self.docker_image = docker_image or "python:3.9-slim"
        
        # Inicjalizacja sandboxu00f3w
        self.python_sandbox = PythonSandbox()
        self.docker_sandbox = DockerSandbox(base_image=self.docker_image) if use_docker else None
        
        # Informacje o systemie
        self.system_info = get_system_info()
        
        logger.info(f"Zainicjalizowano SandboxManager (use_docker={use_docker})")
        if use_docker:
            logger.info(f"Uu017cywany obraz Docker: {self.docker_image}")

    def run_code(self, code: str, timeout: int = 30, force_docker: bool = None) -> Dict[str, Any]:
        """Uruchamia kod Python w odpowiednim sandboxie.

        Args:
            code: Kod Python do uruchomienia.
            timeout: Limit czasu wykonania w sekundach.
            force_docker: Wymusza uu017cycie Dockera (True) lub lokalnego u015brodowiska (False).
                          Jeu015bli None, uu017cywane jest ustawienie z inicjalizacji.

        Returns:
            Dict[str, Any]: Wyniki wykonania kodu.
        """
        use_docker = self.use_docker if force_docker is None else force_docker
        
        if use_docker and self.docker_sandbox:
            logger.info("Uruchamianie kodu w kontenerze Docker...")
            result = self.docker_sandbox.run_code(code, timeout)
        else:
            logger.info("Uruchamianie kodu lokalnie...")
            result = self.python_sandbox.run_code(code, timeout)
        
        # Add system_info if not already present for backward compatibility
        if 'system_info' not in result:
            result['system_info'] = self.system_info
        
        return result

    def format_result(self, result: Dict[str, Any]) -> str:
        """Formatuje wynik wykonania kodu do czytelnej postaci.

        Args:
            result: Su0142ownik z wynikami wykonania kodu.

        Returns:
            str: Sformatowany wynik wykonania kodu.
        """
        return format_execution_result(result)

    def get_sandbox(self, use_docker: bool = None) -> Union[PythonSandbox, DockerSandbox]:
        """Zwraca odpowiedni sandbox.

        Args:
            use_docker: Czy zwru00f3ciu0107 sandbox Dockera. Jeu015bli None, uu017cywane jest ustawienie z inicjalizacji.

        Returns:
            Union[PythonSandbox, DockerSandbox]: Instancja sandboxa.
        """
        use_docker = self.use_docker if use_docker is None else use_docker
        
        if use_docker and self.docker_sandbox:
            return self.docker_sandbox
        else:
            return self.python_sandbox

    @staticmethod
    def from_env() -> 'SandboxManager':
        """Tworzy instancju0119 SandboxManager na podstawie zmiennych u015brodowiskowych.

        Returns:
            SandboxManager: Instancja SandboxManager.
        """
        use_docker = os.environ.get('USE_DOCKER', 'False').lower() in ('true', '1', 't')
        docker_image = os.environ.get('DOCKER_IMAGE', 'python:3.9-slim')
        
        return SandboxManager(use_docker=use_docker, docker_image=docker_image)
