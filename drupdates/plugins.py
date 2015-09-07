""" Plugin ultilities class. """
import imp, os
from drupdates.settings import DrupdatesError
from os.path import expanduser

class Plugin(object):
    """ Simple Plugin system.

    This is shamelessly based on:
    http://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/
    """

    def __init__(self):
        self._main_module = "__init__"
        self._plugins = self.get_plugins()

    def get_plugins(self):
        """ Collect Plugins from the plugins folder. """
        plugin_folders = []
        plugin_folders.append(os.path.dirname(os.path.realpath(__file__)) + "/plugins")
        plugin_folders.append(os.path.join(expanduser('~'), '.drupdates', 'plugins'))
        plugins = {}
        for plugin_folder in plugin_folders:
            if not os.path.isdir(plugin_folder):
                continue
            possibleplugins = os.listdir(plugin_folder)
            for i in possibleplugins:
                location = os.path.join(plugin_folder, i)
                if not os.path.isdir(location) or not self._main_module + ".py" in os.listdir(location):
                    continue
                info = imp.find_module(self._main_module, [location])
                plugins[i] = ({"name": i, "info": info})
        return plugins

    def load_plugin(self, plugin_name):
        """ Load an individual plugin. """
        try:
            plugin = self._plugins[plugin_name]
        except KeyError as error:
            msg = "Unable to find plugin {0}, ensure it exists".format(error)
            raise DrupdatesError(30, msg)
        return imp.load_module(self._main_module, *plugin["info"])
