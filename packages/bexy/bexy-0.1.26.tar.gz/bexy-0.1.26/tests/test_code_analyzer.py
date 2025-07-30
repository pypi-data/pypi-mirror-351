import pytest
from bexy.code_analyzer import CodeAnalyzer


def test_code_analyzer_initialization():
    """Test that CodeAnalyzer initializes correctly."""
    analyzer = CodeAnalyzer()
    assert hasattr(analyzer, 'std_lib_modules')
    assert isinstance(analyzer.std_lib_modules, set)
    assert len(analyzer.std_lib_modules) > 0


def test_extract_imports_simple():
    """Test extracting imports from simple code."""
    code = """
    import os
    import sys
    from datetime import datetime
    """
    analyzer = CodeAnalyzer()
    imports = analyzer.extract_imports(code)
    assert 'os' in imports
    assert 'sys' in imports
    assert 'datetime' in imports


def test_extract_imports_with_comments():
    """Test extracting imports with comments in the code."""
    code = """
    # This is a comment
    import os  # This is an inline comment
    # import sys  # This is a commented import
    from datetime import datetime
    """
    analyzer = CodeAnalyzer()
    imports = analyzer.extract_imports(code)
    assert 'os' in imports
    assert 'sys' not in imports  # Should not extract commented imports
    assert 'datetime' in imports


def test_is_standard_library():
    """Test checking if a module is part of the standard library."""
    analyzer = CodeAnalyzer()
    assert analyzer.is_standard_library('os')
    assert analyzer.is_standard_library('sys')
    assert analyzer.is_standard_library('datetime')
    assert not analyzer.is_standard_library('numpy')  # Not a standard library
    assert not analyzer.is_standard_library('pandas')  # Not a standard library
