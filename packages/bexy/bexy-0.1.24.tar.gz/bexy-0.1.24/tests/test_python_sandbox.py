import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from bexy.python_sandbox import PythonSandbox


def test_python_sandbox_initialization():
    """Test that PythonSandbox initializes correctly."""
    sandbox = PythonSandbox()
    assert hasattr(sandbox, 'dependency_manager')


@patch('tempfile.NamedTemporaryFile')
@patch('subprocess.run')
def test_run_code_success(mock_run, mock_temp_file):
    """Test running code successfully."""
    # Setup mock temporary file
    mock_file = MagicMock()
    mock_file.__enter__.return_value.name = '/tmp/test_code.py'
    mock_temp_file.return_value = mock_file
    
    # Setup mock subprocess run
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = b'Test output'
    mock_process.stderr = b''
    mock_run.return_value = mock_process
    
    sandbox = PythonSandbox()
    result = sandbox.run_code('print("Hello, World!")')
    
    assert result['success'] is True
    assert 'Test output' in result['output']
    assert result['error'] == ''


@patch('tempfile.NamedTemporaryFile')
@patch('subprocess.run')
def test_run_code_with_error(mock_run, mock_temp_file):
    """Test running code that produces an error."""
    # Setup mock temporary file
    mock_file = MagicMock()
    mock_file.__enter__.return_value.name = '/tmp/test_code.py'
    mock_temp_file.return_value = mock_file
    
    # Setup mock subprocess run
    mock_process = MagicMock()
    mock_process.returncode = 1
    mock_process.stdout = b''
    mock_process.stderr = b'NameError: name \'undefined_variable\' is not defined'
    mock_run.return_value = mock_process
    
    sandbox = PythonSandbox()
    result = sandbox.run_code('print(undefined_variable)')
    
    assert result['success'] is False
    assert result['output'] == ''
    assert "NameError" in result['error']


@patch('tempfile.NamedTemporaryFile')
@patch('subprocess.run')
@patch('bexy.dependency_manager.DependencyManager.check_dependencies')
@patch('bexy.dependency_manager.DependencyManager.install_dependencies')
def test_run_code_with_dependencies(mock_install, mock_check, mock_run, mock_temp_file):
    """Test running code with dependencies."""
    # Setup mocks
    mock_file = MagicMock()
    mock_file.__enter__.return_value.name = '/tmp/test_code.py'
    mock_temp_file.return_value = mock_file
    
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = b'Test output'
    mock_process.stderr = b''
    mock_run.return_value = mock_process
    
    mock_check.return_value = (['os', 'sys'], ['numpy'])
    mock_install.return_value = True
    
    sandbox = PythonSandbox()
    result = sandbox.run_code('import numpy as np\nprint(np.array([1, 2, 3]))')
    
    assert result['success'] is True
    assert mock_check.called
    assert mock_install.called
    assert 'numpy' in mock_install.call_args[0][0]
