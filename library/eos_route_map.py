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
module: eos_route_map
version_added: "2.7"
author: "Peter Sprygada (@privateip)"
short_description: Configure route maps on Arista EOS devices
description:
  - This module will configure route-map entries on ARista EOS devices.
options:
  name:
    description:
      - Configures the name of the route-map in the current active
        configuration of the device.
    required: true
  entries:
    description:
      - Configures one or more route-map entries for the named route-map
    type: list
    suboptions:
      rule:
        description:
          - Configures the type of rule to add to the route-map
        required: true
        choices:
          - permit
          - deny
      seqno:
        description:
          - Sets the rule sequence number within the route-map
        required: true
        type: int
      description:
        description:
          - Configures an arbitrary text description for the rule entry in the
            route-map
        required: false
        default: null
      include_route_map:
        description:
          - Sets the rule to include another named route-map
        required: false
        default: null
      continue:
        description:
          - Configures the rule with a continue statement.  This argument is
            mutually exclusive with the C(continue_seqno) argument.
        required: false
        default: null
        type: bool
      continue_seqno:
        description:
          - Sets the next sequence number to continue to for this rule.  This
            argument is mutually exclusive with C(continue)
        required: false
        default: null
        type: int
      match_ip_address_prefix_list:
        description:
          - Configures the name of the prefix-list to match in the rule.
        required: false
        default: null
      match_ip_address_access_list:
        description:
          - Configures the name of the access-list to match in the rule.
        required: false
        default: null
      set_tag:
        description:
          - Configures the name of the tag to set if the rule is matched by a
            match statement.
        required: false
        default: null
        type: int
  replace:
    description:
      - Specifies whether or not the entires configured for this module should
        replace the current route-map entries on the device.
    type: bool
    required: false
    default: null
  state:
    description:
      - Specifies whether or not the named route-map should be present in the
        device active configuration
    default: present
    choices:
      - present
      - absent
"""

EXAMPLES = """
- name: configure a basic route-map
  eos_route_map:
    name: LOOPBACKS
    entries:
      - rule: permit
        seqno: 10
        match_ip_address_prefix_list: LOOPBACKS
    state: present
"""

RETURN = """
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible.module_utils._text import to_text
from ansible.module_utils.eos import check_version


def configure(name, entry):

    commands = list()

    if entry['continue'] is not None and entry['continue_seqno'] is not None:
        raise ValueError('`continue` and `continue_seqno` are mutually exclusive')

    cmd = 'route-map %s' % name
    if entry['rule']:
        cmd += ' %s' % entry['rule']
    if entry['seqno']:
        cmd += ' %s' % entry['seqno']
    commands.append(cmd)

    if entry['description']:
        commands.append('description %s' % entry['description'])

    if entry['include_route_map']:
        commands.append('sub-route-map %s' % entry['include_route_map'])

    if entry['continue'] is not None:
        commands.append('continue')
    elif entry['continue_seqno'] is not None:
        commands.append('continue %s' % entry['continue_seqno'])

    if entry['match_ip_address_prefix_list']:
        commands.append('match ip address prefix-list %s' % entry['match_ip_address_prefix_list'])

    if entry['match_ip_address_access_list']:
        commands.append('match ip address access-list %s' % entry['match_ip_address_access_list'])

    if entry['set_tag']:
        commands.append('set tag %s' % entry['set_tag'])

    return commands


def main():
    """ main entry point for module execution
    """
    entries_spec = {
        'rule': dict(default='permit', choices=['permit', 'deny']),
        'seqno': dict(type='int'),

        'description': dict(),
        'include_route_map': dict(aliases=['sub_route_map']),

        'continue': dict(type='bool'),
        'continue_seqno': dict(type='int'),

        'match_ip_address_prefix_list': dict(),
        'match_ip_address_access_list': dict(),

        'set_tag': dict(type='int')
    }

    argument_spec = dict(
        name=dict(required=True),
        entries=dict(type='list', elements='dict', options=entries_spec),
        replace=dict(type='bool', default=False),
        state=dict(default='present', choices=['present', 'absent'])
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    connection = Connection(module._socket_path)

    if not check_version(connection, 4, 15):
        module.fail_json(msg='failed version check')

    result = {'changed': False}

    commands = list()

    if module.params['state'] == 'absent':
        out = connection.get('show route-map %s' % module.params['name'])
        if out:
            commands.append('no route-map %s' % module.params['name'])

    elif module.params['state'] == 'present':
        if module.params['replace']:
            commands.append('no route-map %s' % module.params['name'])

        try:
            for entry in module.params['entries']:
                commands.extend(configure(module.params['name'], entry))
        except ValueError as exc:
            module.fail_json(msg=to_text(exc))

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
