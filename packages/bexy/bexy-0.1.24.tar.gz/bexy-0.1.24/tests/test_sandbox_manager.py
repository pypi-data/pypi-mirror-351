import pytest
import os
from unittest.mock import patch, MagicMock
from bexy.sandbox_manager import SandboxManager


def test_sandbox_manager_initialization_default():
    """Test that SandboxManager initializes with default settings."""
    manager = SandboxManager()
    assert manager.use_docker is False
    assert manager.docker_image == "python:3.9-slim"


def test_sandbox_manager_initialization_with_docker():
    """Test that SandboxManager initializes with docker enabled."""
    manager = SandboxManager(use_docker=True, docker_image="python:3.10-slim")
    assert manager.use_docker is True
    assert manager.docker_image == "python:3.10-slim"


@patch('bexy.python_sandbox.PythonSandbox.run_code')
def test_run_code_with_python_sandbox(mock_run_code):
    """Test running code with Python sandbox."""
    mock_run_code.return_value = {
        'success': True,
        'output': 'Test output',
        'error': '',
        'execution_time': 0.1
    }
    
    manager = SandboxManager(use_docker=False)
    result = manager.run_code('print("Hello, World!")')
    
    assert result['success'] is True
    assert result['output'] == 'Test output'
    assert result['error'] == ''
    assert 'execution_time' in result
    assert 'system_info' in result


@patch('bexy.docker_sandbox.DockerSandbox.run_code')
def test_run_code_with_docker_sandbox(mock_run_code):
    """Test running code with Docker sandbox."""
    mock_run_code.return_value = {
        'success': True,
        'output': 'Test output from Docker',
        'error': '',
        'execution_time': 0.2
    }
    
    manager = SandboxManager(use_docker=True)
    result = manager.run_code('print("Hello from Docker!")')
    
    assert result['success'] is True
    assert result['output'] == 'Test output from Docker'
    assert result['error'] == ''
    assert 'execution_time' in result
    assert 'system_info' in result


@patch.dict('os.environ', {'USE_DOCKER': 'true'})
def test_from_env_with_docker_enabled():
    """Test creating SandboxManager from environment variables with Docker enabled."""
    manager = SandboxManager.from_env()
    assert manager.use_docker is True


@patch.dict('os.environ', {'USE_DOCKER': 'false'})
def test_from_env_with_docker_disabled():
    """Test creating SandboxManager from environment variables with Docker disabled."""
    manager = SandboxManager.from_env()
    assert manager.use_docker is False


@patch.dict('os.environ', {'DOCKER_IMAGE': 'python:3.11-slim'})
def test_from_env_with_custom_docker_image():
    """Test creating SandboxManager from environment variables with custom Docker image."""
    manager = SandboxManager.from_env()
    assert manager.docker_image == 'python:3.11-slim'
