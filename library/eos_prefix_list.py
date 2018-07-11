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
module: eos_prefix_list
version_added: "2.7"
author: "Peter Sprygada (@privateip)"
short_description: Configure individual entries for prefix lists
description:
  - Configure individual prefix list entries
notes:
  - Tested against EOS 4.15
options:
  name:
    required: true
  entries:
    description:
      - The set of prefix list entries to configure for the named prefix list
    required: false
    defaut: null
    suboptions:
      seqno:
        description:
          - Configures the sequence number for the prefix list entry.
        required: true
        default: null
        type: int
      rule:
        description:
          - Configures the type rule to create at the sequence number
        required: false
        default: true
        choices:
          - permit
          - deny
      prefix:
        description:
          - Sets the IP prefix value to match at this sequence number in the
            prefix list
        required: true
        default: null
      ge:
        description:
          - Configure the netmask length value
        required: false
        default: null
        type: int
      le:
        description:
          - Configure the netmask length value
        required: false
        default: null
        type: int
      eq:
        description:
          - Configure the netmask length value
        required: false
        default: null
        type: int
  replace:
    description:
      - Replaces the current prefix list entries with the ones configured in
        the entries argument.
    required: false
    default: null
  state:
    description:
      - Adds or removes the prefix list from the current device running
        configuration
    default: present
    choices:
      - present
      - absent
"""

EXAMPLES = """
- name: configure basic prefix list
  eos_prefix_list:
    name: TEST
    entries:
      - seqno: 10
        prefix: 10.0.0.0/24
"""

RETURN = """
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible.module_utils.eos import check_version


def configure(entry):

    config = ['seq %s' % entry['seqno'], entry['rule'], entry['prefix']]

    if entry['ge']:
        config.append('ge %s' % entry['ge'])
    elif entry['le']:
        config.append('le %s' % entry['le'])
    elif entry['eq']:
        config.append('eq %s' % entry['eq'])

    return ' '.join(config)


def main():
    """ main entry point for module execution
    """
    entries_spec = dict(
        seqno=dict(type='int', required=True),

        rule=dict(default='permit', choices=['permit', 'deny']),
        prefix=dict(),

        ge=dict(),
        le=dict(),
        eq=dict()
    )

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
        module.fail_json('failed version check')

    result = {'changed': False}

    commands = list()

    if module.params['state'] == 'absent':
        out = connection.get('show ip prefix-list %s' % module.params['name'])
        if out:
            commands.append('no ip prefix-list %s' % module.params['name'])

    elif module.params['state'] == 'present':
        if module.params['replace']:
            commands.append('no ip prefix-list %s' % module.params['name'])

        commands.append('ip prefix-list %s' % module.params['name'])

        out = connection.get('show ip prefix-list %s' % module.params['name'])
        config_lines = out.split('\n')

        for item in module.params['entries']:
            entry = configure(item)

            if entry in config_lines:
                break

            seqno = 'seqno %s' % item['seqno']
            if seqno in out:
                commands.append('no seq %s' % module.params['seqno'])

            commands.append(entry)

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
