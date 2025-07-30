# Foreman
The Foreman service provides a way to manage the Foreman server via the API.

---

## Dependencies

**External Python Packages:**
- apypie


**Configuration File:**

The foreman service requires a configuration file to be present.
By default, the service will look for the configuration file in the current working directory.

However, you can specify the path to the configuration file by passing the `config_file` parameter when initializing
the `Foreman` class.

The configuration file should be named `foreman_config.yml` and should contain the following information:

```yaml
foreman:
  url: 'https://foreman.example.com'
  api_version: 2
create_host:
  build: true
  enabled: true
  hostgroup: foreman.example.com
  interface:
    identifier: eth0
    managed: true
    primary: true
    provision: true
    type: interface
  location: example
  organization: Example Organization
  owner: Foreman-Owners
  owner_type: Usergroup
  provision_method: build
hostgroup_filters:
  filter_by:
    - OS1
    - OS2
  filter_out:
    - OS3
    - OS4
pxe_servers:
  default: 10.0.0.0

```

---

## Installation

To install the `foreman` module you must install `bits-aviso-python-sdk`, use `pip`:

```sh
pip install bits_aviso_python_sdk
```

---

## Usage

### Initialization

To use the `foreman` module, you need to initialize the `Foreman` class with the necessary parameters:

```python
from bits_aviso_python_sdk.services.foreman import Foreman

foreman = Foreman(username='username', password='password', url='https://foreman.example.com')
```


### Examples

TBD

---

## Error Handling
Every function will raise an exception if an error occurs. The main exception is `ValueError`.
The exception will contain the error message returned by the API.

---

# Payloads
The `payloads` module is used to build the payload that will be sent to the Foreman API.

---
