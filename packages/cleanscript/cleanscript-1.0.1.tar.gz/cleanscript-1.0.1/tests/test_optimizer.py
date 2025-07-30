import pytest
from unittest.mock import patch
from cleanscript.optimizer import optimize_code
import ast

def test_basic_optimization():
    """Test basic code optimization functionality."""
    code = '''
import os
import sys

def foo(x):
    return x + 1
'''
    result = optimize_code(code, use_gpt=False)
    
    # Test unused import removal
    assert 'import sys' not in result
    
    # Test docstring addition
    assert any(ds in result for ds in ['Function foo.', '"""Function foo."""', "'''Function foo.'''"])
    
    # Test code functionality is preserved
    assert 'return x + 1' in result
    
    # Verify the output is valid Python
    ast.parse(result)

def test_empty_input():
    """Test behavior with empty input."""
    with pytest.raises(ValueError, match="Empty code provided"):
        optimize_code('', use_gpt=False)
    with pytest.raises(ValueError):
        optimize_code('   \n   \t   ', use_gpt=False)

def test_syntax_error_handling():
    """Test handling of invalid Python code."""
    bad_code = 'def foo(:  # Missing closing parenthesis'
    result = optimize_code(bad_code, use_gpt=False)
    assert "# Syntax error" in result
    assert bad_code in result

@patch('cleanscript.optimizer.generate_comment_gpt')
def test_gpt_comments(mock_gpt):
    """Test GPT comment generation with mock."""
    mock_gpt.return_value = "Mocked GPT comment"
    
    code = 'def bar(): pass'
    result = optimize_code(code, use_gpt=True)
    
    assert 'def bar():' in result
    assert 'Mocked GPT comment' in result
    mock_gpt.assert_called_once()

def test_class_docstrings():
    """Test class docstring generation."""
    code = 'class MyClass: pass'
    result = optimize_code(code, use_gpt=False)
    assert 'Class MyClass.' in result

def test_black_formatting():
    """Verify Black formatting is applied."""
    unformatted = 'def foo():\n    return  {"x":1}'
    result = optimize_code(unformatted, use_gpt=False)
    assert '{"x": 1}' in result  # Black adds space