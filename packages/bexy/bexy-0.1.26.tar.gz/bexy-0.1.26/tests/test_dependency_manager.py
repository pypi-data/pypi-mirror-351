import pytest
import sys
from unittest.mock import patch, MagicMock
from bexy.dependency_manager import DependencyManager


def test_dependency_manager_initialization():
    """Test that DependencyManager initializes correctly."""
    manager = DependencyManager()
    assert hasattr(manager, 'analyzer')
    assert hasattr(manager, 'module_to_package')


def test_create_module_package_mapping():
    """Test that module to package mapping is created correctly."""
    manager = DependencyManager()
    mapping = manager._create_module_package_mapping()
    assert isinstance(mapping, dict)
    assert 'numpy' in mapping
    assert mapping['numpy'] == 'numpy'
    assert 'sklearn' in mapping
    assert mapping['sklearn'] == 'scikit-learn'


@patch('importlib.import_module')
def test_check_module_installed_success(mock_import):
    """Test checking if a module is installed when it is."""
    mock_import.return_value = MagicMock()
    manager = DependencyManager()
    result = manager.check_module_installed('os')
    assert result is True
    mock_import.assert_called_once_with('os')


@patch('importlib.import_module')
def test_check_module_installed_failure(mock_import):
    """Test checking if a module is installed when it is not."""
    mock_import.side_effect = ImportError()
    manager = DependencyManager()
    with patch.object(manager, 'get_installed_packages', return_value=['numpy', 'pandas']):
        result = manager.check_module_installed('nonexistent_module')
        assert result is False


@patch('subprocess.check_call')
def test_install_package_success(mock_check_call):
    """Test installing a package successfully."""
    mock_check_call.return_value = 0
    manager = DependencyManager()
    result = manager.install_package('numpy')
    assert result is True
    mock_check_call.assert_called_once()
    assert [sys.executable, '-m', 'pip', 'install', 'numpy'] in mock_check_call.call_args[0]


@patch('subprocess.check_call')
def test_install_package_failure(mock_check_call):
    """Test installing a package that fails."""
    mock_check_call.side_effect = Exception('Installation failed')
    manager = DependencyManager()
    result = manager.install_package('nonexistent_package')
    assert result is False
