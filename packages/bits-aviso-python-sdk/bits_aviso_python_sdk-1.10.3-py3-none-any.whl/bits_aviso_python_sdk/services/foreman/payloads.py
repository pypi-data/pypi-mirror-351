"""
The `payloads` module is used to build the payload that will be sent to the Foreman API.

---
"""
import logging
from bits_aviso_python_sdk.helpers import check_dict_keys
from bits_aviso_python_sdk.helpers.files import parse_config


def get_interfaces_attribute(ip, mac_address, domain, subnet_id, mtu, config_file):
    """Builds the interfaces attribute for the VM.

    Args:
        ip (string): The ip address of the VM.
        mac_address (string): The mac address of the VM.
        domain (string): The domain id.
        subnet_id (int): The vlan id.
        mtu (int): The mtu of the vlan.
        config_file (str): The path to the config file.

    Returns:
        dict: The interfaces attribute dict for foreman.
    """
    identifier = parse_config(config_file, keys=['create_host', 'interface', 'identifier'])
    managed_flag = parse_config(config_file, keys=['create_host', 'interface', 'managed'])
    primary_flag = parse_config(config_file, keys=['create_host', 'interface', 'primary'])
    provision_flag = parse_config(config_file, keys=['create_host', 'interface', 'provision'])
    type_info = parse_config(config_file, keys=['create_host', 'interface', 'type'])

    return {
        "domain_id": domain,
        "identifier": identifier,
        "ip": ip,
        "mac": mac_address,
        "managed": managed_flag,
        "mtu": mtu,
        "primary": primary_flag,
        "provision": provision_flag,
        "subnet_id": subnet_id,
        "type": type_info,
    }


def get_owner_information(foreman, config_file):
    """Grabs the owner information from the config file.

    Args:
        foreman (Foreman): The Foreman class object.
        config_file (str): The path to the config file.

    Returns:
        string: The owner information.
    """
    owner_type = parse_config(config_file, keys=['create_host', 'owner_type'])
    if owner_type == 'Usergroup':
        owner = foreman.get_current_user()['usergroups'][0]['name']
        resource = 'usergroups'

    elif owner_type == 'User':
        owner = parse_config(config_file, keys=['create_host', 'owner'])
        resource = 'users'

    else:
        logging.error(
            'Unknown owner type. Setting default owner value: Foreman-Admins.')
        owner = 'Foreman-Admins'
        resource = 'usergroups'

    return owner, resource


def create_host_payload(vm_data, foreman, config_file):
    """Complies and calculates VM data into a pretty json payload ready for Foreman's create API.
    The VM data dict is expected to have the following keys:
    ```json
    {
       "name": "vm-name",
        "ip": "10.0.0.0",
        "mac_address": "00:00:00:00:00:00",
        "os": "RHEL 9.4",
        "department": "ADMINISTRATION > BITS",
        "purpose": "states the vm's purpose",
        "assigned_users": "username1, username2",
        "incident": "INC1234567",
        "network": "Portgroup 200",
        "puppet_branch": "staging",
    }
    ```

    Args:
        vm_data (dict): The VM class object.
        foreman (Foreman): The Foreman class object.
        config_file (str): The path to the config file.

    Returns:
        dict: The json payload for Foreman's create API.
    """
    # check for required keys
    check_dict_keys(vm_data, ['name', 'ip', 'mac_address', 'os', 'department', 'purpose', 'assigned_users',
                              'incident', 'network', 'puppet_branch'])

    # get default values from config
    build_flag = parse_config(config_file, keys=['create_host', 'build'])
    enabled_flag = parse_config(config_file, keys=['create_host', 'enabled'])
    location = parse_config(config_file, keys=['create_host', 'location'])
    organization = parse_config(config_file, keys=['create_host', 'organization'])
    owner_type = parse_config(config_file, keys=['create_host', 'owner_type'])
    provision_method = parse_config(config_file, keys=['create_host', 'provision_method'])

    # set puppet environment fields
    hpe = {
        "hidden_value": False,
        "name": "host_puppet_environment",
        "parameter_type": "string",
        "value": f"{vm_data['puppet_branch']}"
    }
    pe = {
        "hidden_value": False,
        "name": "puppet_environment",
        "parameter_type": "string",
        "value": f"{vm_data['puppet_branch']}"
    }

    # get hostgroup info dict
    hostgroup_data = foreman.get_resource_by_name('hostgroups', vm_data['os'])
    hostgroup_architecture = hostgroup_data['inherited_architecture_id']
    hostgroup_domain = hostgroup_data['inherited_domain_id']
    hostgroup_id = hostgroup_data['id']
    hostgroup_medium = hostgroup_data['inherited_medium_id']
    hostgroup_ptable = hostgroup_data['inherited_ptable_id']

    # get vlan data
    subnet_data = foreman.get_resource_by_name('subnets', vm_data['network'])
    subnet_id = subnet_data['id']
    subnet_mtu = subnet_data['mtu']

    # get interface data
    interface = get_interfaces_attribute(vm_data['ip'], vm_data['mac_address'], hostgroup_domain, subnet_id,
                                         subnet_mtu, config_file)

    # get owner information
    owner, owner_resource = get_owner_information(foreman, config_file)

    # build and return the payload
    return {
        "location_id": foreman.get_resource_id_by_name('locations', location),
        "organization_id": foreman.get_resource_id_by_name('organizations', organization),
        "host": {
            "name": vm_data['name'],
            "architecture_id": hostgroup_architecture,
            "build": build_flag,
            "comment": vm_data['incident'],
            "domain_id": hostgroup_domain,
            "enabled": enabled_flag,
            "hostgroup_id": hostgroup_id,
            "host_parameters_attributes": [hpe, pe],
            "interfaces_attributes": [interface],
            "ip": vm_data['ip'],
            "location_id": foreman.get_resource_id_by_name('locations', location),
            "mac": vm_data['mac_address'],
            "medium_id": hostgroup_medium,
            "organization_id": foreman.get_resource_id_by_name('organizations', organization),
            "owner_id": foreman.get_resource_id_by_name(owner_resource, owner),
            "owner_type": owner_type,
            "provision_method": provision_method,
            "ptable_id": hostgroup_ptable,
            "subnet_id": subnet_id,
        }
    }
