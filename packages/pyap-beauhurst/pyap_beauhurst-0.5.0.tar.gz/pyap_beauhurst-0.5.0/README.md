# Pyap: Python address parser

Pyap is an MIT Licensed text processing library, written in Python, for detecting and parsing addresses. Currently it supports US 🇺🇸, Canadian 🇨🇦 and British 🇬🇧 addresses.

This fork is maintained by [Beauhurst](https://github.com/Beauhurst).

## Installation
Install via pip:
```commandline
pip install pyap_beauhurst
```

## Usage
```python
import pyap_beauhurst

# some text with an address in it
test_address = """
Lorem ipsum
225 E. John Carpenter Freeway,
Suite 1500 Irving, Texas 75062
Dorem sit amet
"""

# Parse the text for US addresses
addresses = pyap_beauhurst.parse(test_address, country='US')
for address in addresses:
    # shows found address
    print(address)
    # shows address parts
    print(address.model_dump())
```
