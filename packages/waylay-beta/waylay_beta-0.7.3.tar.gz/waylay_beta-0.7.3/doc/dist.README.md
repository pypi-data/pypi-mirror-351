
# waylay-beta

> ⚠️ This package is **DEPRECATED**.
> Please migrate to [waylay-sdk](https://pypi.org/project/waylay-sdk)

This Python SDK helps you to connect with the REST APIs of the Waylay Platform.

It provides a selection of services and utilities, focused on supporting our data science users:
* importing and querying _timeseries_ data.
* uploading your own _machine learning models_ for usage in the _Waylay Rule Engine_
* provisioning waylay _resources_ and _resource types_.

The SDK is optimised for interactive usage in [Jupyter Notebooks](https://jupyter.org/).

## Prerequisites
This package requires a python runtime `3.9` or higher (validated up to `3.11`). 
For datascience purposes you typically want to prepare an anaconda environment:
```bash
conda create --name my_waylay_env python=3.11
conda activate my_waylay_env
conda install jupyter
pip install waylay-beta
jupyter notebook 
```

## Installation

```bash
pip install waylay-beta
```

### BYOML dependencies

If you want to prepare BYOML models ([Enterprise](http://docs.waylay.io/#/features/byoml/)), _extra_ dependency configurations are available, that will check or install framework-specific dependencies.

Either for a specific runtime:
> $RUNTIME_EXTRA_LIST

or for the default runtime of one of the supported frameworks:
> $FRAMEWORK_EXTRA_LIST

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

## Quickstart

* Login to the waylay console, and get hold of an _API key, API secret_ pair \[*>Settings>Authentication keys*\] 
  > `[Enterprise]` [https://console.waylay.io](https://console.waylay.io/administration/settings/keys)

* Create an SDK client
  ```python
  from waylay import WaylayConfig, WaylayClient
  waylay_client = WaylayClient.from_profile()
  ```
  On first usage, this will prompt for a gateway endpoint,
  > `[Enterprise]` api.waylay.io (default)

  and your _API key/API secret_ credentials. 

For more details see 
> `[Enterprise]` [https://docs.waylay.io](https://docs.waylay.io/#/api/sdk/python)

## Usage Examples
See [demo notebooks](https://github.com/waylayio/demo-general/tree/master/python-sdk) for the usage examples supported in the current release.