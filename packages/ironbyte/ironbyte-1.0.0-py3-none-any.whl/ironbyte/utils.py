import sys

def validate_python_version():
    """Ensure Python version is 3.6+"""
    if sys.version_info < (3, 6):
        raise RuntimeError("IronByte requires Python 3.6 or higher")