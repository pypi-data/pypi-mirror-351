import unittest
from ironbyte import obfuscate, execute

class TestObfuscation(unittest.TestCase):
    def test_obfuscation_and_execution(self):
        source = """
def hello():
    print("Hello, World!")

hello()
"""
        obfuscated = obfuscate(source)
        # Test that the obfuscated code executes properly
        self.assertIsNone(execute(obfuscated))
    
    def test_irreversibility(self):
        source = "x = 42"
        obfuscated = obfuscate(source)
        # Verify the original code isn't easily recoverable
        self.assertNotIn("x = 42", obfuscated)