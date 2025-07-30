import os
from bits_aviso_python_sdk.services.foreman import Foreman

if __name__ == "__main__":
    passwd = os.environ.get('password')
    f = Foreman("https://foreman-dev.broadinstitute.org", username='sa-mnguyen', password=passwd,
                config_file="bits_aviso_python_sdk/tests/configs/foreman_config.yml")
    vm_data = {
        "name": "test-sdk",
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
    f.create_host(vm_data)
