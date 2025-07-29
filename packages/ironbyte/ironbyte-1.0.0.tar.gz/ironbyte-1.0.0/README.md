# IronByte

IronByte is a Python library for irreversible code obfuscation, designed to protect your intellectual property while allowing code execution.

## Features

- Irreversible obfuscation of Python code
- Secure execution of obfuscated code
- Lightweight with no external dependencies

## Installation

```bash
pip install ironbyte
```
## Usage
```bash
from ironbyte import obfuscate, execute
```
# Obfuscate your code
source_code = '''
def hello():
    print("Hello, World!")

hello()
'''

obfuscated_code = obfuscate(source_code)

# Execute obfuscated code
execute(obfuscated_code)