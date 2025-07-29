import ast
import base64
import zlib
import marshal
import random
import string
from types import CodeType

def _random_name(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def _transform_code_object(code_obj):
    consts = []
    for const in code_obj.co_consts:
        if isinstance(const, CodeType):
            consts.append(_transform_code_object(const))
        else:
            consts.append(const)
    
    # Ensure all CodeType arguments are properly converted
    return CodeType(
        code_obj.co_argcount,                     # int
        code_obj.co_posonlyargcount,              # int (added in Python 3.8)
        code_obj.co_kwonlyargcount,               # int
        code_obj.co_nlocals,                      # int
        code_obj.co_stacksize,                    # int
        code_obj.co_flags,                        # int
        code_obj.co_code,                         # bytes
        tuple(consts),                            # tuple
        code_obj.co_names,                        # tuple
        code_obj.co_varnames,                     # tuple
        code_obj.co_filename,                     # str
        _random_name(),                           # str (original: code_obj.co_name)
        code_obj.co_firstlineno,                  # int
        code_obj.co_lnotab,                       # bytes
        code_obj.co_freevars,                     # tuple
        code_obj.co_cellvars                      # tuple
    )

def obfuscate(source_code, compression_level=9):
    """
    Obfuscate Python source code irreversibly.
    
    Args:
        source_code (str): Python source code to obfuscate
        compression_level (int): Zlib compression level (1-9)
    
    Returns:
        str: Obfuscated code that can be executed with IronByte.execute()
    """
    # Parse and compile the code
    tree = ast.parse(source_code)
    code_obj = compile(tree, '<string>', 'exec')
    
    # Transform code objects
    transformed_code = _transform_code_object(code_obj)
    
    # Serialize and compress
    serialized = marshal.dumps(transformed_code)
    compressed = zlib.compress(serialized, level=compression_level)
    
    # Base64 encode for safe string representation
    encoded = base64.b64encode(compressed).decode('utf-8')
    
    # Generate loader template
    loader_template = f"""
import base64
import zlib
import marshal

def _ironbyte_execute():
    encoded = "{encoded}"
    compressed = base64.b64decode(encoded.encode('utf-8'))
    serialized = zlib.decompress(compressed)
    code_obj = marshal.loads(serialized)
    exec(code_obj)

_ironbyte_execute()
"""
    return loader_template