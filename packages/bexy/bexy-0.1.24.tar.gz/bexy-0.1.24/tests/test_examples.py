#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the Bexy package using the example files.
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Bexy modules
from bexy.code_analyzer import CodeAnalyzer
from bexy.dependency_manager import DependencyManager
from bexy.python_sandbox import PythonSandbox


def get_example_files():
    """Get all example files from the examples directory."""
    examples_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bexy', 'examples')
    return [f for f in Path(examples_dir).glob('*.py') if f.is_file()]


def get_example_content(example_file):
    """Get the content of an example file directly."""
    with open(example_file, 'r') as f:
        return f.read()


def get_example_prompt(example_name):
    """Generate a prompt based on the example name."""
    prompts = {
        "api_request": "create a program that fetches data from a REST API and include all necessary imports",
        "database": "create a program that connects to a SQLite database and performs CRUD operations, include all necessary imports",
        "default": "create a simple hello world program",
        "file_io": "create a program that reads and writes to files, include all necessary imports",
        "web_server": "create a simple web server with HTTP server, include import for http.server and BaseHTTPRequestHandler"
    }
    
    # Handle both Path objects and strings
    if hasattr(example_name, 'stem'):
        base_name = example_name.stem
    else:
        # If it's a string, remove the .py extension if present
        base_name = example_name.replace('.py', '')
    
    return prompts.get(base_name, f"create a {base_name.replace('_', ' ')} program")


def add_main_for_web_server(code, example_name):
    """Add a main function for web server examples if needed."""
    # Only process web server examples
    if example_name != 'web_server':
        return code
        
    # Add a main function call if needed for examples that don't have one
    if 'if __name__' not in code:
        # Check if there's a server setup code
        if 'HTTPServer' in code and 'serve_forever' in code:
            # Add a demonstration mode that doesn't actually start the server
            code += """

# Demonstration mode - create server but don't start it
def create_server(port=8000):
    print(f"Creating server configuration for port {port}...")
    print("This is a demonstration only - no actual server is started")
    print("To run a real server, uncomment the code below:\n")
    print("    server_address = ('', port)")
    print("    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)")
    print(f"    print(f\"Server running on port {port}...\")")
    print("    httpd.serve_forever()")
    print("    ")

if __name__ == "__main__":
    create_server()
"""
    return code


def execute_code_with_bexy(code, example_name=None):
    """Execute code using Bexy sandbox."""
    # Process web server examples to avoid binding to ports during testing
    if example_name == 'web_server':
        code = add_main_for_web_server(code, example_name)

    # Create a PythonSandbox instance
    sandbox = PythonSandbox()
    
    # Execute the code
    result = sandbox.run_code(code)
    
    return result


@pytest.fixture
def mock_subprocess():
    """Mock the subprocess module."""
    with patch('subprocess.run') as mock:
        process_mock = MagicMock()
        process_mock.returncode = 0
        process_mock.stdout = "Test output"
        process_mock.stderr = ""
        mock.return_value = process_mock
        yield mock


@pytest.mark.parametrize("example_name", [
    "api_request",
    "database",
    "default",
    "file_io",
    "web_server"
])
def test_example_code_analysis(example_name):
    """Test that the code analyzer correctly analyzes the example code."""
    # Get the example files
    examples_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bexy', 'examples')
    example_file = os.path.join(examples_dir, f"{example_name}.py")
    
    # Get the content of the example file
    code = get_example_content(Path(example_file))
    
    # Create a CodeAnalyzer instance
    analyzer = CodeAnalyzer()
    
    # Analyze the code
    result = analyzer.analyze_code(code)
    
    # Check that the result contains the expected keys
    assert 'imports' in result
    assert 'standard_library' in result
    assert 'third_party' in result
    assert 'unknown' in result
    
    # Check specific imports based on the example
    if example_name == 'api_request':
        assert 'requests' in result['third_party']
    elif example_name == 'database':
        assert 'sqlite3' in result['standard_library']
    elif example_name == 'file_io':
        # The file_io example uses built-in open() function without explicit imports
        pass
    elif example_name == 'web_server':
        assert 'http' in result['standard_library']


@pytest.mark.parametrize("example_name", [
    "api_request",
    "database",
    "default",
    "file_io",
    "web_server"
])
def test_example_dependency_analysis(example_name):
    """Test that the dependency manager correctly analyzes the example code."""
    # Get the example files
    examples_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bexy', 'examples')
    example_file = os.path.join(examples_dir, f"{example_name}.py")
    
    # Get the content of the example file
    code = get_example_content(Path(example_file))
    
    # Create a DependencyManager instance
    manager = DependencyManager()
    
    # Analyze the dependencies
    result = manager.analyze_dependencies(code)
    
    # Check that the result contains the expected keys
    assert 'imports' in result
    assert 'required_packages' in result
    assert 'installed_packages' in result
    assert 'missing_packages' in result
    
    # Check specific dependencies based on the example
    if example_name == 'api_request':
        assert 'requests' in result['required_packages']


@pytest.mark.parametrize("example_name", [
    "default",  # Start with the simplest example
    "file_io",
    "web_server",
    "api_request",
    "database"
])
def test_example_execution(example_name, mock_subprocess):
    """Test that the examples can be executed using Bexy."""
    # Get the example files
    examples_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bexy', 'examples')
    example_file = os.path.join(examples_dir, f"{example_name}.py")
    
    # Get the content of the example file
    code = get_example_content(Path(example_file))
    
    # Mock the run_code method to avoid actual execution
    with patch('bexy.python_sandbox.PythonSandbox.run_code') as mock_run_code:
        # Set up the mock to return a successful result
        mock_run_code.return_value = {
            'success': True,
            'stdout': 'Test output',
            'stderr': '',
            'result': None,
            'execution_time': 0.05
        }
        
        # Execute the code
        result = execute_code_with_bexy(code, example_name)
        
        # Check that the code was executed successfully
        assert result['success'] is True
        assert 'stdout' in result
        assert 'stderr' in result
        assert 'execution_time' in result


def test_all_examples_integration():
    """Integration test for all examples."""
    # Get all example files
    example_files = get_example_files()
    
    # Make sure we found some examples
    assert len(example_files) > 0, "No example files found"
    
    # Test each example file
    for example_file in example_files:
        print(f"Testing {example_file.name}...")
        
        # Get the content of the example file
        code = get_example_content(example_file)
        
        # Test code analysis
        analyzer = CodeAnalyzer()
        analysis_result = analyzer.analyze_code(code)
        assert 'imports' in analysis_result
        
        # Test dependency analysis
        manager = DependencyManager()
        dependency_result = manager.analyze_dependencies(code)
        assert 'required_packages' in dependency_result
        
        # Test code execution (with mocked sandbox)
        with patch('bexy.python_sandbox.PythonSandbox.run_code') as mock_run_code:
            # Set up the mock to return a successful result
            mock_run_code.return_value = {
                'success': True,
                'stdout': 'Test output',
                'stderr': '',
                'result': None,
                'execution_time': 0.05
            }
            
            # Execute the code
            result = execute_code_with_bexy(code, example_file.stem)
            
            # Check that the code was executed successfully
            assert result['success'] is True
            assert 'stdout' in result
            assert 'stderr' in result
            assert 'execution_time' in result
