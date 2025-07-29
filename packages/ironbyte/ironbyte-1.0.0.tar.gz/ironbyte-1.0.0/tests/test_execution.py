import unittest
from ironbyte import execute

class TestExecution(unittest.TestCase):
    def test_execute_obfuscated(self):
        # This is a pre-obfuscated version of `print(1+1)`
        obfuscated_code = """
import base64
import zlib
import marshal
import types

def _ironbyte_execute():
    encoded = "eJxLtDKyUijISVVIK8pJLVJIzkksSVVIysxL10jOLMpJLElVBADp6QqE"
    compressed = base64.b64decode(encoded.encode('utf-8'))
    serialized = zlib.decompress(compressed)
    code_obj = marshal.loads(serialized)
    exec(code_obj)

_ironbyte_execute()
"""
        # Redirect stdout to capture print output
        import io
        from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            execute(obfuscated_code)
        self.assertEqual(f.getvalue().strip(), "2")