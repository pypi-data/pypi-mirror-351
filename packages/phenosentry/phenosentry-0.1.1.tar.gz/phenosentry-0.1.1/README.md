# phenosentry

A Python package for ensuring data quality in phenopackets and collections of phenopackets.

## Features

- Load phenopacket stores from the phenopacket-store or ZIP archives
- Load any phenopacket or phenopackets from a folder into a phenopacket store
- Validate phenopacket stores with quality checks

## Installation

Install with [Poetry](https://python-poetry.org/):

```bash
poetry add phenosentry
```
or with pip:

```bash
pip install phenosentry
```

# Usage

```python
from phenosentry.model import DefaultPhenopacketStore
from phenosentry.validation import default_auditor

# Load a phenopacket store from a folder
store = DefaultPhenopacketStore.from_folder("path/to/phenopackets")

# Get the default auditor
auditor = default_auditor()

# Prepare a notepad for auditing
notepad = auditor.prepare_notepad("my-store")

# Audit the phenopacket store
auditor.audit(item=store, notepad=notepad)

if notepad.has_errors_or_warnings():
    print("Issues found in phenopacket store!")
else:
    print("Phenopacket store passed all checks.")
```

# Development
Run tests with:

```bash
pytest
```

# License 
MIT License