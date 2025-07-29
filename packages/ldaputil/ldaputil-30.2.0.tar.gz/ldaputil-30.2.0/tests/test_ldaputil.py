"""
Tests for ldaputil package
"""

import unittest
from unittest.mock import patch
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestLdaputil(unittest.TestCase):
    
    def test_hello_world_function(self):
        """Test hello_world function"""
        from ldaputil import hello_world
        
        with patch('builtins.print') as mock_print:
            result = hello_world()
            mock_print.assert_called_with("Hello World from ldaputil package!")
            self.assertEqual(result, "Hello World!")
    
    def test_greet_function(self):
        """Test greet function from main module"""
        from ldaputil.main import greet
        
        with patch('builtins.print') as mock_print:
            result = greet("Test")
            mock_print.assert_called_with("Hello Test from ldaputil!")
            self.assertEqual(result, "Hello Test from ldaputil!")
    
    def test_greet_default(self):
        """Test greet function with default parameter"""
        from ldaputil.main import greet
        
        with patch('builtins.print') as mock_print:
            result = greet()
            mock_print.assert_called_with("Hello World from ldaputil!")
            self.assertEqual(result, "Hello World from ldaputil!")

if __name__ == '__main__':
    unittest.main() 