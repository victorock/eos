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
module: eos_bgp_address_family
version_added: "2.7"
author: "Peter Sprygada (@privateip)"
short_description: Configure BGP address-family parameters
description:
  - Add and remove BGP address families from the global BGP routing process
    running on Arista EOS devices.  This module will also active or deactive
    specific neighbors.
options:
  afi:
    description:
      - Specify the BGP address family to configure in the global BGP routing
        process.
    required: true
    choices:
      - ipv4
      - ipv6
      - evpn
  neighbors:
    description:
      - Configure the set of BGP neighbors (either peer groups or direct
        neighbors) associated with the named adress family identifier.
    type: list
    required: false
    suboptions:
      name:
        description:
          - The name of the neighbor to configure for the specified
            address-family.  This value can be either the neighbor IP address
            or peer-group name
        required: true
      activate:
        description:
          - Enables or disables the address-family for the neighbor
        required: false
        type: bool
        default: none
  replace:
   state:
    description:
      - Specifies the desired state of the address family within the global
        BGP routing process.
    default: present
    choices:
      - present
      - active
"""

EXAMPLES = """
- name: active evpn for neighbors LEAF
  eos_bgp_address-family:
    afi: evpn
    neighbors:
      - name: LEAF
        activate: yes

- name: replace all activated neighbors with the configured values
  eos_bgp_address_family:
    afi: ipv4
    neighbors:
      - name: 10.1.1.1
        activate: yes
    replace: yes
"""

RETURN = """
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible.module_utils.bgp import get_bgp_as


def configure(module):
    commands = list()

    for entry in module.params['neighbors']:
        name = entry['name']

        if entry['activate'] is True:
            commands.append('neighbor %s activate' % name)
        elif entry['activate'] is False:
            commands.append('no neighbor %s activate' % name)

    return commands


def main():
    """ main entry point for module execution
    """
    neighbors_spec = {
        'name': dict(required=True),
        'activate': dict(type='bool')
    }


    argument_spec = {
        'afi': dict(required=True, choices=['ipv4', 'ipv6', 'evpn']),

        'neighbors': dict(type='list', elements='dict', options=neighbors_spec),

        'replace': dict(type='bool'),
        'state': dict(default='present', choices=['present', 'absent'])
    }

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    connection = Connection(module._socket_path)

    bgp_as = get_bgp_as(connection)

    if not bgp_as:
        module.fail_json(msg='bgp not configured on this node')

    result = {'changed': False}

    commands = list()

    if module.params['state'] == 'absent':
        commands.extend([
            'router bgp %s' % bgp_as,
            'no address-family %s' % module.params['afi'],
            'exit'
        ])

    else:
        commands.append('router bgp %s' % bgp_as)

        if module.params['replace']:
            commands.append('no address-family %s' % module.params['afi'])

        commands.append('address-family %s' % module.params['afi'])
        commands.extend(configure(module))
        commands.append('exit')

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
