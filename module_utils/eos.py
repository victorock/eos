import json

def get_capabilities(connection):
    return json.loads(connection.get_capabilities())



def check_version(connection, maj_version=None, min_version=None):
    capabilities = get_capabilities(connection)

    majver = int(capabilities['device_info']['network_os_version'].split('.')[0])
    minver = int(capabilities['device_info']['network_os_version'].split('.')[1])

    if maj_version:
        if not majver >= maj_version:
            return False

    if min_version:
        if not minver >= min_version:
            return False

    return True


