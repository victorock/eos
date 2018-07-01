===============================
eos
===============================

v1.2.0
======

Major Changes
-------------

- Introduces ``lldp`` as a facts subset when running ``get_facts`` function

- Now checks for the connection type to be set to ``network_cli`` in the
  ``get_facts`` function and returns and error if it is not


v1.1.0
======

New Functions
-------------

- NEW ``get_facts`` Collect Ansible facts from device

v1.0.0
======

Major Changes
-------------

- Initial release of the ``eos`` role.

- This role provides a set of functions for working with Arista EOS based
  devices for performing operational and configuration tasks


New Functions
-------------

- NEW ``clear_sessions`` Clears all configuration sessions found on the device

