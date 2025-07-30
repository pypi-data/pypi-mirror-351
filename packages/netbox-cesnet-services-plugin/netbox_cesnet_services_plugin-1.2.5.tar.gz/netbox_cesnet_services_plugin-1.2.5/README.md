# NetBox cesnet_services Plugin

NetBox plugin for CESNET services.

* Free software: MIT
* Documentation: https://kani999.github.io/netbox-cesnet-services-plugin/


## Features

Enables CESNET services in Netbox. BGP connections, LLDP Neigbors, LLDP Leafs

## Compatibility

| NetBox Version | Plugin Version |
|----------------|----------------|
|     4.3.1      |      1.2.4     |
|     4.3.1      |      1.2.3     |
|     4.2.8      |      1.2.2     |

## Installing

For adding to a NetBox Docker setup see
[the general instructions for using netbox-docker with plugins](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

You can install with pip:

```bash
pip install netbox-cesnet-services-plugin
```

or by adding to your `local_requirements.txt` or `plugin_requirements.txt` (netbox-docker):

```bash
netbox-cesnet-services-plugin==1.2.3
```

Enable the plugin in `/opt/netbox/netbox/netbox/configuration.py`,
 or if you use netbox-docker, your `/configuration/plugins.py` file :

Set device platforms for filtering choices in LLDPNeighbor form. 

```python
PLUGINS = [
    'netbox_cesnet_services_plugin'
]

PLUGINS_CONFIG = {
    "netbox_cesnet_services_plugin": {
        "platforms" : ["ios", "iosxe", "iosxr", "nxos", "nxos_ssh"],
    },
}
```

## Credits

Based on the NetBox plugin tutorial:

- [demo repository](https://github.com/netbox-community/netbox-plugin-demo)
- [tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin) project template.
