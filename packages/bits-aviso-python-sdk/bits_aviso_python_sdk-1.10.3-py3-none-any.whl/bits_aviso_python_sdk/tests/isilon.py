from bits_aviso_python_sdk.helpers.files import write_json
from bits_aviso_python_sdk.services.isilon import Isilon
from bits_aviso_python_sdk.services.google.secretmanager import SecretManager


def test():
    """Manually test the Isilon class."""
    secret_manager = SecretManager()
    google_project = ''
    credentials_secret = ''
    clusters_secret = ''
    credentials = secret_manager.get_secret(google_project, credentials_secret)
    clusters = secret_manager.get_secret(google_project, clusters_secret)
    username = credentials.get('username')
    password = credentials.get('password')
    isilon = Isilon(username, password, clusters)
    quota_data, _ = isilon.get_entity_for_all_clusters('quotas', '/quota/quotas')
    write_json(quota_data, 'quotas.json')


if __name__ == '__main__':
    test()
