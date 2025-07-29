"""
Provides utilities to retrieve internal and external plugins.
"""

import pluggy

from mafw import hookspecs, plugins

global_mafw_plugin_manager: dict[str, pluggy.PluginManager] = {}


def get_plugin_manager(force_recreate: bool = False) -> pluggy.PluginManager:
    """
    Create a new or return an existing plugin manager for a given project

    :param force_recreate: Flag to force the creation of a new plugin manager. Defaults to False
    :type force_recreate: bool, Optional
    :return: The plugin manager
    :rtype: pluggy.PluginManager
    """
    if 'mafw' in global_mafw_plugin_manager and force_recreate:
        del global_mafw_plugin_manager['mafw']

    if 'mafw' not in global_mafw_plugin_manager:
        pm = pluggy.PluginManager('mafw')
        pm.add_hookspecs(hookspecs)
        pm.load_setuptools_entrypoints('mafw')
        pm.register(plugins)
        global_mafw_plugin_manager['mafw'] = pm

    return global_mafw_plugin_manager['mafw']
