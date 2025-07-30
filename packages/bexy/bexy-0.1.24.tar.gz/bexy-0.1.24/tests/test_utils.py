import pytest
import platform
import os
from unittest.mock import patch, MagicMock
from bexy.utils import get_system_info, format_execution_result, ensure_dependencies


def test_get_system_info():
    """Test that get_system_info returns the correct system information."""
    info = get_system_info()
    assert 'python_version' in info
    assert 'platform' in info
    assert 'os' in info
    assert info['python_version'] == platform.python_version()
    assert info['platform'] == platform.platform()
    assert info['os'] == platform.system()


def test_format_execution_result_success():
    """Test formatting a successful execution result."""
    result = {
        'success': True,
        'output': 'Test output',
        'error': '',
        'execution_time': 0.1,
        'system_info': {
            'python_version': '3.9.0',
            'platform': 'Linux',
            'os': 'Linux'
        }
    }
    
    formatted = format_execution_result(result)
    assert 'SUCCESS' in formatted
    assert 'Test output' in formatted
    assert 'Execution time: 0.1 seconds' in formatted
    assert 'Python 3.9.0' in formatted


def test_format_execution_result_failure():
    """Test formatting a failed execution result."""
    result = {
        'success': False,
        'output': '',
        'error': 'NameError: name \'undefined_variable\' is not defined',
        'execution_time': 0.05,
        'system_info': {
            'python_version': '3.9.0',
            'platform': 'Linux',
            'os': 'Linux'
        }
    }
    
    formatted = format_execution_result(result)
    assert 'ERROR' in formatted
    assert 'NameError' in formatted
    assert 'Execution time: 0.05 seconds' in formatted


@patch('bexy.dependency_manager.DependencyManager.check_dependencies')
@patch('bexy.dependency_manager.DependencyManager.install_dependencies')
def test_ensure_dependencies_all_installed(mock_install, mock_check):
    """Test ensuring dependencies when all are already installed."""
    mock_check.return_value = (['numpy', 'pandas'], [])
    
    result = ensure_dependencies(['numpy', 'pandas'])
    
    assert result is True
    assert mock_check.called
    assert not mock_install.called


@patch('bexy.dependency_manager.DependencyManager.check_dependencies')
@patch('bexy.dependency_manager.DependencyManager.install_dependencies')
def test_ensure_dependencies_some_missing(mock_install, mock_check):
    """Test ensuring dependencies when some are missing."""
    mock_check.return_value = (['numpy'], ['pandas'])
    mock_install.return_value = True
    
    result = ensure_dependencies(['numpy', 'pandas'])
    
    assert result is True
    assert mock_check.called
    assert mock_install.called
    assert ['pandas'] == mock_install.call_args[0][0]


@patch('bexy.dependency_manager.DependencyManager.check_dependencies')
@patch('bexy.dependency_manager.DependencyManager.install_dependencies')
def test_ensure_dependencies_installation_failure(mock_install, mock_check):
    """Test ensuring dependencies when installation fails."""
    mock_check.return_value = (['numpy'], ['pandas'])
    mock_install.return_value = False
    
    result = ensure_dependencies(['numpy', 'pandas'])
    
    assert result is False
    assert mock_check.called
    assert mock_install.called
