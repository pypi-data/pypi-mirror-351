"""
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
"""
import apypie
import logging
import re
import requests
from bits_aviso_python_sdk.helpers import check_dict_keys
from bits_aviso_python_sdk.helpers.files import parse_config
from bits_aviso_python_sdk.services.foreman import payloads
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

from bits_aviso_python_sdk.services.foreman.payloads import create_host_payload

logger = logging.getLogger(__name__)


class Foreman:
    """Class object to interact with Foreman via API. Requires user credentials to auth to the API."""

    def __init__(self, url, username, password, api_version=2, config_file="foreman_config.yml"):
        """Constructor for the Foreman object. Requires user credentials to auth to the API via a python Session object.
        A config file is also required in order to manage values for the Foreman API.
        Please see the README for more info.

        Args:
            url (string): The base url of the Foreman instance.
            username (string): The user's foreman username.
            password (string): The user's foreman password.
            api_version (int, optional): The version of the Foreman API to use. Defaults to 2.
            config_file (string, optional): The path to the config file. Defaults to "foreman_config.yml".

        """
        self.username = username
        self.password = password
        self.url = url
        self.api_version = api_version
        self.api = apypie.Api(username=self.username, password=self.password, uri=self.url,
                              api_version=self.api_version)
        self.config_file = config_file

    def create_host(self, vm_data):
        """Creates a host in Foreman via API.
        The vm_data dict must contain the following keys:
        ```json
        {
            "name": "vm-name",
            "assigned_users": "username1, username2",
            "department": "ADMINISTRATION > BITS",
            "incident": "INC1234567",
            "ip": "10.0.0.0",
            "mac_address": "00:00:00:00:00:00",
            "network": "Portgroup 200",
            "os": "RHEL 9.4",
            "puppet_branch": "staging",
            "purpose": "states the vm's purpose",
        }
        ```

        Args:
            vm_data (dict): The vm data dict.

        Raises:
            ValueError: If the host creation fails.
        """
        # check for the mandatory keys
        check_dict_keys(vm_data, ['name', 'assigned_users', 'department', 'incident', 'ip', 'mac_address',
                                  'network', 'os', 'puppet_branch', 'purpose'])

        logger.info(f'Creating {vm_data["name"]} as a host in Foreman...')

        try:
            payload = create_host_payload(vm_data, self, self.config_file)
            self.api.resource('hosts').action('create').call(params=payload)
            logging.info(f'Host {vm_data["name"]} has been created in Foreman.')

        except HTTPError as e:
            error_message = f'Unable to create host {vm_data["name"]}. | {e}'
            logger.error(error_message)
            raise ValueError(error_message)

    def filter_hostgroups(self, filter_by=None):
        """Filters the list of hostgroups based on their title.

        Args:
            filter_by (list, optional): The list of hostgroups to filter by. Defaults to None.

        Returns:
            list[dict]: A list containing all the filtered OS's.

        Raises:
            ValueError: If the hostgroups cannot be filtered.
        """
        # grab the filters
        if filter_by is None:
            try:
                filter_by = parse_config(self.config_file, keys=['hostgroup_filters', 'filter_by'])
            except (KeyError, FileNotFoundError) as e:
                error_message = f'Unable to get hostgroup filter from config file. | {e}'
                logger.error(error_message)
                raise ValueError(error_message)

        # grab all the hostgroups
        hostgroups = self.list_hostgroups()

        # check if there are any hostgroups before proceeding
        if not hostgroups:
            logger.error('No hostgroups were found in Foreman. Nothing to filter.')

        filtered_hostgroups = []

        # filter out the hostgroups we dont care about
        for hg in hostgroups:
            try:
                # first filter out the parent hostgroups
                if hg['parent_id'] is None:
                    continue
                else:
                    for fb in filter_by:
                        if fb.lower() in hg['title'].lower():
                            filtered_hostgroups.append(hg)

            except (AttributeError, KeyError):
                continue

        return filtered_hostgroups

    def get_current_user(self):
        """Grabs the current user's data from Foreman.
        This uses requests bc apypie doesn't have a method for this.
        Thanks for nothing.

        Returns:
            dict: The current user's data.
        """
        try:
            user = requests.get(f"{self.url}/api/current_user",
                                auth=HTTPBasicAuth(self.username, self.password))
            user.raise_for_status()  # raise an exception if the request fails
            return user.json()

        except HTTPError as e:
            error_message = f'Unable to get current user. | {e}'
            logger.error(error_message)
            raise ValueError(error_message)

    def get_latest_hostgroup_version(self, classification):
        """Function to grab the latest hostgroup from Foreman.

        Args:
            classification (string): The classification of the hostgroup to grab.

        Returns:
            string: The latest hostgroup's name.

        Raises:
            ValueError: If the latest hostgroup cannot be found.
        """
        # configure filters from config file, if none, set to empty list
        filter_out = parse_config(self.config_file, keys=['hostgroup_filters', 'filter_out'], allow_none=True)
        if not filter_out:
            filter_out = []

        # mysql and docker are special cases, there's no dedicated hostgroup for it
        if classification == 'mysql' or classification == 'docker':
            classification = 'rhel'

        # grab list of os's from foreman and parse it to get data
        filtered_hostgroups = self.filter_hostgroups()
        major, minor = 0, 0
        latest = {}

        logger.debug(f'Retrieving the latest {classification} version from Foreman...')

        # check if there are any hostgroups before proceeding
        if not filtered_hostgroups:
            error_message = 'Unable to get latest hostgroup version.'
            logger.error(error_message)
            raise ValueError(error_message)

        # filter out the hostgroups we dont care about
        hostgroups = [
            fh for fh in filtered_hostgroups
            if all(substring.lower() not in fh['title'].lower() for substring in filter_out)
            and classification.lower() in fh['title'].lower()
        ]

        # check if there are any hostgroups before proceeding
        if not hostgroups:
            error_message = f'No {classification} hostgroups were found.'
            logger.error(error_message)
            raise ValueError(error_message)

        # get the latest hostgroup
        for hostgroup in hostgroups:
            hg_major, hg_minor = map(
                int, re.findall(r"\d+", hostgroup['title']))

            # check if the current hostgroup is the latest
            if hg_major > major or (hg_major == major and hg_minor > minor):
                major, minor = hg_major, hg_minor
                latest = hostgroup

        try:
            logger.info(f'The latest {classification} OS is {latest["name"]}.')
            return latest['name']

        except KeyError:
            error_message = f'Unable to find the latest {classification} OS.'
            logger.error(error_message)
            raise ValueError(error_message)

    def get_resource_by_name(self, resource, name, search=None):
        """Grabs the resource's respective data.

        Args:
            resource (string): The resource type of the item to get the data of.
            name (string): The name of the resource to get the data of.
            search (string): The search term to filter the results by. Defaults to None.

        Returns:
            dict: The resource's data.

        Raises:
            ValueError: If the resource data cannot be found.
        """
        try:
            if search:
                resources = self.api.resource(resource).action(
                    'index').call({'per_page': 100, 'search': search})
            else:
                resources = self.api.resource(resource).action(
                    'index').call({'per_page': 100})
            if resources is not None:
                for r in resources['results']:
                    if r['name'] == name:
                        return r
            else:
                raise KeyError

        except KeyError:
            error_message = f'Unable to get data for the resource {name}.'
            logger.error(error_message)
            raise ValueError(error_message)

    def get_resource_id_by_name(self, resource, name, search=None):
        """Grabs the resource's respective ID.

        Args:
            resource (string): The resource type of the item to get the ID of.
            name (string): The name of the resource to get the ID of.
            search (string): The search term to filter the results by. Defaults to None.

        Returns:
            int: The resource's ID. Returns -1 if no ID is found.

        Raises:
            ValueError: If the resource ID cannot be found.
        """
        try:
            if search:
                resources = self.api.resource(resource).action(
                    'index').call({'per_page': 100, 'search': search})
            else:
                resources = self.api.resource(resource).action(
                    'index').call({'per_page': 100})

            if resources is not None:
                for r in resources['results']:
                    if r['name'] == name:
                        return r['id']
            else:
                raise KeyError

        except KeyError:
            error_message = f'Unable to get ID for the resource {name}.'
            logger.error(error_message)
            raise ValueError(error_message)

    def list_common_parameters(self):
        """Lists all the global parameters in Foreman via API.

        Returns:
            list[dict]: A list containing all common parameter data in Foreman.

        Raises:
            ValueError: If the common parameters cannot be retrieved.
        """
        logger.debug('Retrieving list of all common parameters in Foreman...')
        try:
            common_parameters = self.api.resource(
                'common_parameters').action('index').call({'per_page': 100})
            if common_parameters is not None:
                return common_parameters['results']
            else:
                raise KeyError

        except KeyError:
            error_message = 'Unable to retrieve common parameters from Foreman.'
            logger.error(error_message)
            raise ValueError(error_message)

    def list_hostgroups(self):
        """Lists all the available hostgroups in Foreman via API.

        Returns:
            list[dict]: The list of hostgroups.

        Raises:
            ValueError: If the hostgroups cannot be retrieved.
        """
        logger.debug("Retrieving list of all hostgroups in Foreman...")
        try:
            hostgroups = self.api.resource('hostgroups').action(
                'index').call({'per_page': 100})

            if hostgroups is not None:
                return hostgroups['results']
            else:
                raise KeyError

        except KeyError:
            error_message = 'Unable to retrieve hostgroups from Foreman.'
            logger.error(error_message)
            raise ValueError(error_message)

    def list_subnets(self):
        """Lists all the subnets in Foreman via API.

        Returns:
            list[dict]: A list containing all subnet data in Foreman.

        Raises:
            ValueError: If the subnets cannot be retrieved
        """
        logger.debug('Retrieving list of all subnets in Foreman...')
        try:
            subnets = self.api.resource('subnets').action(
                'index').call({'per_page': 100})
            if subnets is not None:
                return subnets['results']
            else:
                raise KeyError

        except KeyError:
            error_message = 'Unable to retrieve subnets from Foreman.'
            logger.error(error_message)
            raise ValueError(error_message)
