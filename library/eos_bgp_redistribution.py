#!/usr/bin/python
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}


DOCUMENTATION = """
---
module: eos_bgp_redistribution
version_added: "2.7"
author: "Peter Sprygada (@privateip)"
short_description: Configure route redistribution into the BGP process
description:
  - This module provides configuration of BGP route redistribution into the
    global BGP routing process running on Arista EOS devices.
options:
  protocol:
    description:
      - Specifies the protocol routes to redistribute into BGP
    required: true
    choices:
      - connected
      - static
  route_map:
    description:
      - Configures the name of the route-map to apply to the routes being
        redistributed into BGP
    required: false
    default: null
  state:
    description:
      - Specifies whether or not the named protocol should be redistributed
        into the BGP routing process.
    default: present
    choices:
      - present
      - absent
"""

EXAMPLES = """
- name: redistribute connected routes
  eos_bgp_redistribution:
    protocol: connected
    state: present

- name: redistribute static routes with route-map
  eos_bgp_redistribution:
    protocol: static
    route_map: ROUTES
    state: present
"""

RETURN = """
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible.module_utils.bgp import get_bgp_as


def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        protocol=dict(required=True, choices=['connected', 'static']),
        route_map=dict(),
        state=dict(default='present', choices=['present', 'absent'])
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    connection = Connection(module._socket_path)

    bgp_as = get_bgp_as(connection)

    result = {'changed': False}

    commands = list()

    if module.params['state'] == 'absent':
        commands.extend([
            'router bgp %s' % bgp_as,
            'no redistribute %s' % module.params['protocol'],
            'exit'
        ])

    elif module.params['state'] == 'present':
        commands.extend([
            'router bgp %s' % bgp_as,
            'no redistribute %s' % module.params['protocol']
        ])
        cmd = 'redistribute %s' % module.params['protocol']
        if module.params['route_map'] is not None:
            cmd += ' route-map %s' % module.params['route_map']
        commands.extend([cmd, 'exit'])

    if commands:
        commit = not module.check_mode
        resp = connection.load_config(commands, commit)
        if resp.get('diff'):
            result['changed'] = True
            if module._diff:
                result['diff'] = {'prepared': resp['diff']}

    module.exit_json(**result)

if __name__ == '__main__':
    main()
