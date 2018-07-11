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
module: eos_bgp
version_added: "2.7"
author: "Peter Sprygada (@privateip)"
short_description: Configure global BGP protocol settings on Arista EOS
description:
  - This module provides configuration management of global BGP parameters
    on devices running Arista EOS.
notes:
  - Tested against EOS 4.15
options:
  bgp_as:
    description:
      - Specifies the BGP Autonomous System number to configure on the device
    type: int
    required: true
  router_id:
    description:
      - Configures the BGP routing process router-id value
    default: null
  maximum_paths:
    description:
      - Configures the maximum equal cost paths to install
    type: int
    default: null
  state:
    description:
      - Specifies the state of the BGP process configured  on the device
    default: present
    choices:
      - present
      - absent
"""

EXAMPLES = """
- name: configure global bgp as 65000
  eos_bgp:
    bgp_as: 65000
    router_id: 1.1.1.1
    state: present

- name: remove bgp as 65000 from config
  eos_bgp:
    bgp_as: 65000
    state: absent
"""

RETURN = """
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible.module_utils.bgp import get_bgp_as


def configure(module):
    commands = list()

    if module.params['router_id']:
        commands.append('router-id %s' % module.params['router_id'])

    if module.params['maximum_paths']:
        commands.append('maximum-paths %s' % module.params['maximum_paths'])

    if commands:
        commands.insert(0, 'router bgp %s' % module.params['bgp_as'])

    return commands


def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        bgp_as=dict(required=True, type='int'),

        router_id=dict(),
        maximum_paths=dict(type='int'),

        state=dict(default='present', choices=['present', 'absent'])
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    connection = Connection(module._socket_path)
    bgp_as = get_bgp_as(connection)

    result = {'changed': False}

    commands = list()

    if module.params['state'] == 'absent':
        commands.append('no router bgp %s' % module.params['bgp_as'])

    elif module.params['state'] == 'present':
        if bgp_as and bgp_as != module.params['bgp_as']:
            commands.append('no router bgp %s' % bgp_as)
        commands.extend(configure(module))

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
