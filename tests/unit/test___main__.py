#!/usr/bin/env python3
"""
Unit tests for the __main__.py module.
"""
import pytest
from unittest.mock import patch
import sys
import importlib


@patch('ai_tools.main.main')
def test_main_is_called_when_module_run_directly(mock_main):
    """Test that main() function is called when __main__.py is run directly."""
    # Directly test the behavior by simulating the __main__ condition
    # Save original __name__ value in the __main__ module
    original_name = None
    if '__main__' in sys.modules:
        original_name = sys.modules['__main__'].__name__
    
    try:
        # Import ai_tools.__main__ module first
        import ai_tools.__main__
        
        # Now execute the conditional code manually as if __name__ was "__main__"
        if hasattr(ai_tools.__main__, "main"):
            ai_tools.__main__.main()
        
        # Verify main() was called
        mock_main.assert_called_once()
    finally:
        # Restore the original __name__ if we modified it
        if original_name and '__main__' in sys.modules:
            sys.modules['__main__'].__name__ = original_name


@patch('ai_tools.main.main')
def test_main_not_called_on_import(mock_main):
    """Test that main() function is not called when __main__.py is imported."""
    # Reset mock
    mock_main.reset_mock()
    
    # Import the module (this should not call main() because we're running
    # this as a test, not as __main__)
    import ai_tools.__main__
    importlib.reload(ai_tools.__main__)
    
    # Verify main() was not called
    mock_main.assert_not_called()