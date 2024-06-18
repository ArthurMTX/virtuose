import socket
import libvirt
import time
import requests
from django.http import JsonResponse

from Virtuose.settings import API_URL, QEMU_URI


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


def interact_with_domain(dom_uuid, action):
    url = f"{API_URL}/domains/actions/{dom_uuid}/{action}"
    response = requests.post(url)

    if response.status_code == 200:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': response.text})


def get_dom_object(dom_uuid):
    conn = libvirt.open(QEMU_URI)
    dom = conn.lookupByUUIDString(dom_uuid)
    return dom


def wait_for_vm_to_be_ready(vm_uuid, timeout=60):
    vm = get_domain_by_uuid(vm_uuid)
    if vm is None:
        return False

    start_time = time.time()
    while time.time() - start_time < timeout:
        if vm.isActive() and check_guest_agent_active(vm_uuid):
            return True
        time.sleep(5)
    return False


def check_guest_agent_active(vm_uuid):
    try:
        vm = get_domain_by_uuid(vm_uuid)
        if vm.isActive() == 0:
            return False

        max_retries = 5
        for attempt in range(max_retries):
            try:
                if vm.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0):
                    return True
            except libvirt.libvirtError:
                pass
            time.sleep(1)
    except libvirt.libvirtError:
        return False
    return False
