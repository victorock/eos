===============================
eos
===============================

devel
=====

Major Changes
-------------

- NEW ``eos_bgp`` module

- NEW ``eos_bgp_redistribution`` module

Minor Changes
-------------

- added config parsers to the ``get_config`` function to parse device config

v.1.3.0
=======

New Functions
-------------

- NEW ``get_config`` Return the device configuration


Major Changes
-------------

- NEW ``eos_capabilities`` module 

Minor Changes
-------------

- Fix dependency entry to properly call ansible-network.network-engine


Minor Changes
-------------

- Device capability facts are now available to the parser templates


v1.2.1
======

Minor Changes
-------------

- updated lldp parser template to expand local port interface name

- updated switchport parser template to expand interface

- moved switchport facts into interface tree

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

