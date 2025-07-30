# A Python library for parsing [OBO(Open Biological and Biomedical Ontologies)](https://obofoundry.org/) files.

## Installation

```
pip install obo_parser
```

## Usage

### Use in Command Line

```bash
obo_parser headers -f path/to/obo_file.obo
obo_parser headers -f path/to/obo_file.obo -o headers.json

obo_parser terms -f path/to/obo_file.obo
obo_parser terms -f path/to/obo_file.obo -o terms.jl
```

### Use in Python

```python
from obo_parser.parser import OBO_Parser

obo = OBO_Parser('./hp.obo')
print(obo.headers)

for term in obo.terms:
    print(term)
```
