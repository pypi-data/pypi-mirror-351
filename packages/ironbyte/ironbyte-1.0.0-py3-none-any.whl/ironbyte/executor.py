import base64
import zlib
import marshal

def execute(obfuscated_code):
    """
    Execute obfuscated IronByte code.
    
    Args:
        obfuscated_code (str): Obfuscated code from IronByte.obfuscate()
    """
    # Extract the encoded string from the obfuscated code
    lines = obfuscated_code.split('\n')
    encoded_line = [line for line in lines if line.strip().startswith('encoded = "')][0]
    encoded = encoded_line.split('"')[1]
    
    # Decode and execute
    compressed = base64.b64decode(encoded.encode('utf-8'))
    serialized = zlib.decompress(compressed)
    code_obj = marshal.loads(serialized)
    exec(code_obj)