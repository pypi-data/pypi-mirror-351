[![CI](https://github.com/waylayio/waylay-py/actions/workflows/ci.yml/badge.svg)](https://github.com/waylayio/waylay-py/actions/workflows/ci.yml)

# waylay-py
Python SDK for the Waylay Platform

## Prerequisites
This package requires a python runtime `3.11`.
For datascience purposes you typically want to prepare a anaconda environment:
```bash
conda create --name my_waylay_env python=3.11
conda activate my_waylay_env
conda install jupyter
pip install waylay-beta # .. or any of the other installation methods below
jupyter notebook 
```

## Installation

### from [Python Package Index](https://pypi.org/project/waylay-beta/)
```bash
pip install waylay-beta
```
### from [this repository](https://github.com/waylayio/waylay-py)
```bash
pip install git+https://github.com/waylayio/waylay-py@v0.4.0
```

### BYOML runtime dependencies
If you want to prepare BYOML models ([Enterprise](http://docs.waylay.io/#/features/byoml/)),
_extra_ dependency configurations are available, that will check or install runtime-specific dependencies.

Use the label `byoml-<framework>-<framework-version>` for a specific runtime version, or
`byoml-<framework>` for the current default for a given framework. 

See [byoml_runtimes.json](doc/byoml_runtimes.json) for the list of supported runtimes.

E.g. to install with sklearn dependencies for byoml:
```bash
pip install waylay-beta['byoml-sklearn-0.24']
```
or
```bash
pip install waylay-beta['byoml-sklearn']
```

In some cases (e.g. older framework versions) it might be needed to use the same python version
when serializing models. Check the supported python version with calls such as:
```python
> waylay_client.byoml.runtimes.get('byoml-pytorch-1.8')
{'framework': 'pytorch', 'framework_version': '1.8', 'name': 'byoml-pytorch-1.8', 'python_version': '3.7'}
```

### from source
```bash
git clone https://github.com/waylayio/waylay-py
pip install -e ./waylay-py
```
See [Development Manual](doc/dev.md) for more details.

## User Documentation

> `[Enterprise]` https://docs.waylay.io/api/sdk/python

## Usage
See [demo notebooks](https://github.com/waylayio/demo-general/tree/master/python-sdk) for usage examples.

## Development
See [Development Manual](doc/dev.md)

## Overview of support API endpoints
See [Supported Endpoints](doc/services.md)
