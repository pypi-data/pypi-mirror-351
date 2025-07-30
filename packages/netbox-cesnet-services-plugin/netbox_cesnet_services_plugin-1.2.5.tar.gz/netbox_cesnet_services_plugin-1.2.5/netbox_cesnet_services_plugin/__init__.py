"""Top-level package for NetBox cesnet_services Plugin."""

__author__ = """Jan Krupa"""
__email__ = "jan.krupa@cesnet.cz"
__version__ = "1.2.5"


from netbox.plugins import PluginConfig


class CesnetServicesConfig(PluginConfig):
    name = "netbox_cesnet_services_plugin"
    verbose_name = "NetBox cesnet_services Plugin"
    description = "NetBox plugin for CESNET services."
    version = __version__
    base_url = "netbox-cesnet-services-plugin"
    author = __author__
    author_email = __email__


config = CesnetServicesConfig
