import re
import json

from ansible.module_utils.six import iteritems

_CACHED_COMMANDS = {}

def get(connection, command):
    try:
        out = _CACHED_COMMANDS[command]
    except KeyError:
        out = connection.get(command)
        if command.endswith('| json'):
            out = json.loads(out)
        _CACHED_COMMANDS[command] = out
    return out


def get_bgp_as(connection):
    out = get(connection, 'show ip bgp summary | json')
    if 'default'in out['vrfs']:
        return int(out['vrfs']['default']['asn'])


def get_bgp_peer_group_neighbors(connection, peer_group):
    out = get(connection, 'show ip bgp peer-group %s' % peer_group)
    matches = re.findall('^\s{6}(\S+),', out, re.M)
    return matches
