"""
The `isilon` module provides a set of tools to interact with Isilon clusters using the PowerScale API.
It includes methods to retrieve and update quotas and network pools for the clusters. The default platform
version is `15`.

---

## Installation

To install the `isilon` module, use `pip`:

```sh
pip install bits_aviso_python_sdk
```

---

## Usage

### Initialization

To use the `isilon` module, you need to initialize the `Isilon` class with the necessary parameters:

```python
from bits_aviso_python_sdk.services.isilon import Isilon

isilon = Isilon(username='username', password='password', clusters=['cluster1', 'cluster2'])
```

### Examples

---

#### Get All Quotas

Retrieve all quotas for all clusters:

```python
all_quotas, errors = isilon.get_entity_for_all_clusters('quotas', '/quota/quotas')
print(all_quotas)
print(errors)
```

---

#### Get All Quotas for a Cluster

Retrieve all quotas in a specific cluster:

```python
quotas, error = isilon.get_entity_for_cluster('cluster1', 'quotas', '/quota/quotas')
print(quotas)
print(error)
```

---

#### Update a Specific Quota

Updates a specific quota. The cluster and quota ID must be provided, along with any parameters you wish to update:

```python
updated_quota, error = isilon.update_quota('cluster1', '8380451k3hjkhjasf', description='new quota description')
print(updated_quota)
print(error)
```
See the [Isilon API documentation](https://developer.dell.com/apis/4088/versions/9.5.0/9.5.0.0_ISLANDER_OAS2.json/paths/~1platform~115~1quota~1quotas~1%7Bv15QuotaQuotaId%7D/put) for more details on the available parameters.

---

#### Get Network Pools for All Clusters

Retrieve network pools for all clusters:

```python
all_network_pools, errors = isilon.get_entity_for_all_clusters('pools', '/network/pools')
print(all_network_pools)
print(errors)
```

---

#### Get Network Pools for a Specific Cluster

Retrieve network pools for a specific cluster:

```python
network_pools, error = isilon.get_entity_for_cluster('cluster1', 'pools', '/network/pools')
print(network_pools)
print(error)
```

---


## Error Handling

Each method returns a tuple containing the result and an error payload.
The error payload will contain details if any errors occurred during the execution of the method.

```json
{
    "Error": "An error message will be here."
}
```

---
"""
import base64
import logging
import requests
import urllib3
from bits_aviso_python_sdk.helpers import resolve_dns

# suppress InsecureRequestWarning
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)


class Isilon:
    """Class to interact with the Isilon PowerScale API."""

    def __init__(self, username, password, clusters=None, platform_api_version='15', dns_resolve=False,
            dns_server=None):
        """Initializes the Isilon class.

        Args:
            username (str): The username to authenticate with.
            password (str): The password to authenticate with.
            clusters (list): A list containing cluster names. Defaults to None.
            platform_api_version (str, optional): The version of the Isilon API to use. Defaults to '15'.
            dns_resolve (bool, optional): Whether to resolve the DNS. Defaults to False.
            dns_server (str, optional): The DNS server to use for resolution. Defaults to None.
        """
        self.clusters = clusters
        self.headers = {'Authorization': f'Basic {self._encode_credentials(username, password)}'}
        self.platform_api_version = platform_api_version
        self.dns_resolve = dns_resolve
        self.dns_server = dns_server

    @staticmethod
    def _encode_credentials(username, password):
        """Encodes the username and password for use in the API.

        Args:
            username (str): The username to authenticate with.
            password (str): The password to authenticate with.

        Returns:
            str: The encoded credentials.
        """
        return base64.b64encode(f'{username}:{password}'.encode()).decode()

    def build_url(self, cluster, api_endpoint=None, api_platform_version=None, resume=None):
        """Builds the URL for the given Isilon cluster with no trailing slash. If an API endpoint is provided,
        it will be appended to the URL.

        Args:
            cluster (str, optional): The cluster name.
            api_endpoint (str, optional): The path to the API endpoint. Defaults to None.
            api_platform_version (str, optional): The version of the Isilon API to use. Defaults to None.
            resume (str, optional): The resume token for pagination. Defaults to None.

        Returns:
            str: The URL for the Isilon API. If DNS resolution fails, None is returned.
        """
        # check if dns resolution is needed
        if self.dns_resolve:
            try:
                cluster_domain = f'{cluster}.broadinstitute.org'
                cluster = resolve_dns(cluster_domain, dns_server=self.dns_server)
                if not cluster:
                    raise ValueError

            except ValueError:
                logging.error(f'Failed to resolve the DNS for {cluster}.')
                return

        # check if a platform API version is provided
        if not api_platform_version:
            api_platform_version = self.platform_api_version

        # check if an API endpoint is provided
        if api_endpoint:
            if api_endpoint.startswith('/'):  # check for a leading slash
                api_endpoint = api_endpoint[1:]  # remove the leading slash bc imma put it MYSELF

            # create the URL with the API endpoint
            url = f'https://{cluster}:8080/platform/{api_platform_version}/{api_endpoint}'

            # check if there is a resume token
            if resume:
                url += f'?resume={resume}'

        else:
            url = f'https://{cluster}:8080/platform/{api_platform_version}'

        return url

    def get_entity_for_all_clusters(self, entity, api_endpoint, api_platform_version=None, clusters=None):
        """Gets the specified entity for all clusters.

        Args:
            entity (str): The entity to get (e.g., 'quotas', 'network pools').
            api_endpoint (str): The API endpoint to use for the entity.
            api_platform_version (str, optional): The version of the Isilon API to use. Defaults to None.
            clusters (list, optional): A list containing the cluster names. Defaults to None.

        Returns:
            list[dict], dict: The entity data for all clusters and error payload if any.
        """
        all_entities = []
        error_payload = {}

        # if no clusters are provided, use the clusters from the class
        if not clusters:
            if not self.clusters:
                error_payload['Error'] = 'No clusters provided. Unable to get any entities.'
                return [], error_payload
            else:
                clusters = self.clusters

        for cluster in clusters:
            cluster_entity, error_payload = self.get_entity_for_cluster(cluster, entity, api_endpoint,
                                                                        api_platform_version=api_platform_version)
            if cluster_entity:
                all_entities.extend(cluster_entity)

            elif error_payload:
                error_payload.update(cluster_entity)

            else:
                error_payload['Error'] = f'Failed to get {entity} data for the cluster {cluster}.'

        return all_entities, error_payload

    def get_entity_for_cluster(self, cluster_name, entity, api_endpoint, api_platform_version=None):
        """Gets the specified entity for the given cluster.

        Args:
            cluster_name (str): The cluster's name.
            entity (str): The entity to get. This should be the same as the key in the JSON response of the API.
            api_endpoint (str): The API endpoint to use for the entity. This is the path to the API endpoint after
                                the platform version.
            api_platform_version (str, optional): The version of the Isilon API to use. Defaults to None.

        Returns:
            list[dict], dict: The entity data for the cluster and error payload if any.
        """
        entities = []
        resume = None
        max_iterations = 50
        iteration = 0

        while True:
            # check if the maximum iterations are reached
            if iteration >= max_iterations:
                err_msg = f'Maximum iterations reached for {entity} on {cluster_name}.'
                logging.error(err_msg)
                return [], {"Error": err_msg}

            # update loop iteration
            iteration += 1

            # build the url
            url = self.build_url(cluster_name, api_endpoint=api_endpoint, api_platform_version=api_platform_version,
                                 resume=resume)

            try:
                if not url:
                    raise ValueError(f'Failed to build the URL for {cluster_name} with the api endpoint {api_endpoint}')

                # call the api
                response = requests.get(url, headers=self.headers, verify=False)
                response.raise_for_status()
                entity_json = response.json()
                resume = entity_json.get('resume')

                # check if the entity is in the response
                entity_data = entity_json.get(entity)

                # check if there is any entity data
                if entity_data:
                    for e in entity_data:
                        e['cluster'] = cluster_name  # add the cluster name to the entity data
                        entities.append(e)  # add the entity data to the list

                    # check if there is pagination
                    if not resume:
                        return entities, {}

                else:
                    # if there are no entities at all, raise an error
                    if not entities:
                        raise ValueError(f'No {entity} data found for {cluster_name}.')

            except (requests.exceptions.RequestException, ValueError) as e:
                err_msg = f'Failed to get {entity} for {cluster_name}.\nException Message: {e}'
                logging.error(err_msg)
                return [], {"Error": err_msg}

    def get_quota_data(self, cluster_name, path, list_of_quotas=None):
        """Gets the quota data for the given path.
        If a list of quotas is provided, it will be used instead of fetching the quotas from the cluster.

        Args:
            cluster_name (str): The cluster's name.
            path (str): The path to get the quota data for.
            list_of_quotas (list[dict], optional): The list of quotas to search through. Defaults to None.

        Returns:
            dict, dict: The quota data for the path and error payload if any.
        """
        if list_of_quotas:  # if a list of quotas is provided, use it
            quotas = list_of_quotas

        else:  # if not, get the quota data for the cluster
            quotas, error_payload = self.get_entity_for_cluster(cluster_name, 'quotas', '/quota/quotas')

            # check if there are any quotas
            if not quotas:
                return {}, error_payload

        # find the quota data for the path
        for quota in quotas:
            if quota.get('path') == path:
                return quota, {}

        return {}, {"Error": f'No quota data found for the path {path}'}

    def get_quota_id(self, cluster_name, path, list_of_quotas=None):
        """Gets the quota id for the given path.
        If a list of quotas is provided, it will be used instead of fetching the quotas from the cluster.

        Args:
            cluster_name (str): The cluster's name.
            path (str): The path to get the quota id for.
            list_of_quotas (list[dict], optional): The list of quotas to search through. Defaults to None.

        Returns:
            str, dict: The quota id for the path and error payload if any.
        """
        if list_of_quotas:  # if a list of quotas is provided, use it
            quotas = list_of_quotas

        else:  # if not, get the quota data for the cluster
            quotas, error_payload = self.get_entity_for_cluster(cluster_name, 'quotas', '/quota/quotas')

            # check if there are any quotas
            if not quotas:
                return '', error_payload

        # find the quota id for the path
        for quota in quotas:
            if quota.get('path') == path:
                return quota.get('id'), {}

        return '', {"Error": f'No quota id found for the path {path}'}

    def update_quota(self, cluster_name, quota_id, **kwargs):
        """Updates the quota data for the given quota id.

        Args:
            cluster_name (str): The cluster's name.
            quota_id (str): The id of the quota to update.
            **kwargs: The quota data to update. The key should be the field to update and the value should the value.

        Returns:
            bool, dict: True if the quota was updated successfully and error payload if any.
        """
        # build the url
        url = self.build_url(cluster_name, f'/quota/quotas/{quota_id}')

        # parse the kwargs into a payload
        payload = {}
        for key, value in kwargs.items():
            payload[key] = value

        try:
            # check if the url was built successfully
            if not url:
                raise ValueError(f'Failed to build the URL for {cluster_name}')

            # update the quota data
            response = requests.put(url, headers=self.headers, verify=False, json=payload)
            response.raise_for_status()
            return True, {}

        except (requests.exceptions.RequestException, ValueError, TypeError) as e:
            err_msg = (f'Failed to update quota for {quota_id}. Cluster: {cluster_name}\n'
                       f'Exception Message: {e}')
            logging.error(err_msg)
            return {}, {"Error": err_msg}
