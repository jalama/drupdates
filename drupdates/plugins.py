""" Plugin ultilities class. """
import imp, os

class Plugin(object):
    """ Simple Plugin system.

    This is shamelessly based on:
    http://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/
    """

    def __init__(self):
        self._plugin_folder = os.path.dirname(os.path.realpath(__file__)) + "/plugins"
        self._main_module = "__init__"
        self._plugins = self.get_plugins()

    def get_plugins(self):
        """ Collect Plugins from the plugins folder. """
        plugins = {}
        possibleplugins = os.listdir(self._plugin_folder)
        for i in possibleplugins:
            location = os.path.join(self._plugin_folder, i)
            if not os.path.isdir(location) or not self._main_module + ".py" in os.listdir(location):
                continue
            info = imp.find_module(self._main_module, [location])
            plugins[i] = ({"name": i, "info": info})
        return plugins

    def load_plugin(self, plugin):
        """ Load an individual plugin. """
        return imp.load_module(self._main_module, *plugin["info"])
