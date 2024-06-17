import socket
import requests
from Virtuose.settings import API_URL


def get_free_port():
    for port in range(6080, 6981):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                pass
    return None


def get_all_domains():
    response = requests.get(f"{API_URL}/domains/")
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_domain_by_uuid(uuid):
    response = requests.get(f"{API_URL}/domains/UUID/{uuid}")
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_domain_by_name(name):
    response = requests.get(f"{API_URL}/domains/{name}")
    if response.status_code == 200:
        return response.json()
    else:
        return None
