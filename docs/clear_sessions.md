# Clear sessions
The `clear_sessions` function can be used to clear all configuration sessions
on a device running the Arista EOS network operating system.  This function
only works with the `network_cli` connection type and requires the the
`ansible_network_os` value is set to `eos`.  

## How to clear all configuration sessions
In order to properly use this role, the playbook should implement the
`import_role` task and specify the `tasks_from` to be `clear_sessions`.  Below
is an example playbook that will clear all configuration sessions on the target
EOS device.

```
- hosts: arista_eos
  
  tasks:
    - name: clear all configuration sessions
      import_role:
        name: privateip.ansible_eos
        tasks_from: clear_sessions
```

## Requirements
The following is the list of requirements for using the this task:

* Ansible 2.5 or later

## Arguments
The ```clear_sessions``` task has no configurable arguments.

## Notes
None

## Changelog

* 1.0.0 - initial function added to the role

