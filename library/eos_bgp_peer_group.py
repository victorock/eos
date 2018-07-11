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
module: eos_bgp_peer_group
version_added: "2.7"
author: "Peter Sprygada (@privateip)"
short_description: Configure BGP peer groups on Arista EOS devices
description:
  - Provisiong BGP peer groups in the global BGP routing process.
options:
  name:
    description:
      - The name of the peer group to manage in the active configuration
    required: true
  remote_as:
    description:
      - The value for the BGP peer-group remote-as.
    required: false
    default: null
    type: int
  maximum_routes:
    description:
      - The maximum number of routes to install for the peer group
    required: false
    default: null
    type: int
  next_hop_unchanged:
    description:
      - Configures the next hop unchanged value for this name peer group
    required: false
    default: null
    type: bool
  update_source:
    description:
      - Configures the update-source value for the peer group
    required: false
    default: null
  ebgp_multihop:
    description:
      - Configues the ebgp-multihop value to the specific number of hops
    required: false
    default: null
    type: int
  send_community_extended:
    description:
      - Enables or disables the sending of extended community attributes for
        the named peer group
    required: false
    default: null
    type: bool
  neighbors:
    description:
      - Configures the list of neighbors associated with this peer group
    required: false
    default: null
    type: list
  replace:
    description:
      - Specifies the module should replace the entire BGP peer-group entry
        for this peer-group with the provided configuration.
    required: false
    default: null
    type: bool
  negate_on_none:
    description:
      - Setting this value will cause all values that have not been explicitly
        provided to be considered negation statements.
    required: false
    default: null
    type: bool
  state:
    description:
      - Specifies whether or not the peer-group is included in the the BGP
        process
    default: present
    choices:
      - present
      - absent
"""

EXAMPLES = """
- name: configure a new peer group
  eos_bgp_peer_group:
    name: LEAF
    remote_as: 65001
    maximum_routes: 5000
    neighbors:
      - 172.16.10.1
      - 172.16.11.1

- name: remove peer group from configuration
  eos_bgp_peer_group:
    name: LEAF
    state: absent
"""

RETURN = """
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible.module_utils.bgp import get_bgp_as, get_bgp_peer_group_neighbors


def configure(module, bgp_as, neighbors):
    commands = list()

    negate_on_none = module.params['negate_on_none']

    def add(cmd):
        return 'neighbor %s %s' % (module.params['name'], cmd)

    def negate(cmd):
        return 'no %s' % add(cmd)

    if module.params['remote_as']:
        commands.append(add('remote-as %s' % module.params['remote_as']))
    elif negate_on_none:
        commands.append(negate('remote-as'))

    if module.params['maximum_routes']:
        commands.append(add('maximum-routes %s' % module.params['maximum_routes']))
    elif negate_on_none:
        commands.append(negate('maximum-routes'))

    if module.params['next_hop_unchanged'] is True:
        commands.append(add('next-hop-unchanged'))
    elif module.params['next_hop_unchanged'] is False or negate_on_none:
        commands.append(negate('next-hop_unchanged'))

    if module.params['update_source']:
        commands.append(add('update-source %s' % module.params['update_source']))
    elif negate_on_none:
        commands.append(negate('update-source'))

    if module.params['ebgp_multihop'] is not None:
        commands.append(add('ebgp-multihop %s' % module.params['ebgp_multihop']))
    elif negate_on_none:
        commands.append(negate('ebgp-multihop'))

    if module.params['send_community_extended']:
        commands.append(add('send-community extended'))
    elif negate_on_none:
        commands.append(negate('send-community extended'))

    adds = set(module.params['neighbors']).difference(neighbors)
    removes = set(neighbors).difference(module.params['neighbors'])

    for item in adds:
        commands.append('neighbor %s peer-group %s' % (item, module.params['name']))

    for item in removes:
        commands.append('no neighbor %s peer-group')

    if commands:
        commands.insert(0, 'router bgp %s' % bgp_as)

    return commands


def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        name=dict(required=True),

        remote_as=dict(),
        maximum_routes=dict(),

        next_hop_unchanged=dict(type='bool'),
        update_source=dict(type='bool'),
        ebgp_multihop=dict(type='int'),
        send_community_extended=dict(type='bool'),

        neighbors=dict(type='list'),

        replace=dict(type='bool'),
        negate_on_none=dict(type='bool'),

        state=dict(default='present', choices=['present', 'absent'])
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    connection = Connection(module._socket_path)

    name = module.params['name']

    bgp_as = get_bgp_as(connection)
    neighbors = get_bgp_peer_group_neighbors(connection, name)

    if not bgp_as:
        module.fail_json(msg='bgp not configured on this node')

    result = {'changed': False}

    commands = list()

    if module.params['state'] == 'absent':
        commands.extend([
            'router bgp %s' % bgp_as,
            'no neighbor %s' % module.params['name'],
            'exit'
        ])

    else:
        if module.params['replace']:
            commands.append('no neighbor %s' % module.params['name'])
        commands.extend(configure(module, bgp_as, neighbors))

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
