import pytest
from unittest.mock import patch, mock_open, MagicMock
from cleanscript.cli import main
import sys
import os

def test_cli_success(tmp_path, capsys):
    """Test CLI with successful execution."""
    test_file = tmp_path / "test.py"
    test_file.write_text("import os\n\ndef foo(): pass")
    
    with patch('sys.argv', ['cleanscript', str(test_file)]):
        main()
        
    captured = capsys.readouterr()
    assert "Optimization complete" in captured.out
    assert "🚀" in captured.out

def test_cli_output_file(tmp_path):
    """Test CLI with output file specified."""
    input_file = tmp_path / "input.py"
    output_file = tmp_path / "output.py"
    input_file.write_text("def foo(x):\n    return x + 1")
    
    with patch('sys.argv', ['cleanscript', str(input_file), '-o', str(output_file)]):
        main()
        
    assert output_file.exists()
    assert "def foo" in output_file.read_text()
    assert "return x + 1" in output_file.read_text()

def test_cli_nonexistent_file(capsys):
    """Test CLI with non-existent input file."""
    with patch('sys.argv', ['cleanscript', 'nonexistent.py']):
        with pytest.raises(SystemExit):
            main()
    
    captured = capsys.readouterr()
    assert "File not found" in captured.out or "File not found" in captured.err

@patch('cleanscript.cli.optimize_code')
def test_cli_gpt_flag(mock_optimize, tmp_path):
    """Test CLI with --use-gpt flag."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def foo(): pass")
    
    mock_optimize.return_value = "optimized code"
    with patch('sys.argv', ['cleanscript', str(test_file), '--use-gpt']):
        main()
    
    mock_optimize.assert_called_once()
    args, kwargs = mock_optimize.call_args
    assert kwargs['use_gpt'] is True

def test_cli_version(capsys):
    """Test version flag shows only version number."""
    with patch('sys.argv', ['cleanscript', '--version']):
        with pytest.raises(SystemExit):
            main()
    
    captured = capsys.readouterr()
    assert captured.out.strip() == "1.0.0"  # Expect just the version number
    assert captured.err == ""

def test_cli_no_arguments(capsys):
    """Test running with no arguments shows help."""
    with patch('sys.argv', ['cleanscript']):
        with pytest.raises(SystemExit):
            main()
    captured = capsys.readouterr()
    
    # Check for either the colored or uncolored version
    assert ("CleanScript" in captured.out or 
            "╔═╗╦╔═╗╔═╗╔╦╗╦ ╦╔═╗╦╔╦╗╦ ╦╔═╗" in captured.out or
            "The Ultimate Python Code Optimizer & Documenter" in captured.out)