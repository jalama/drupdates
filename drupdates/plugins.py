""" Plugin ultilities class. """
import imp, os, git, requests
from drupdates.settings import DrupdatesError
from drupdates.utils import Utils
from os.path import expanduser
from git import Repo
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


class Plugin(object):
    """ Simple Plugin system.

    This is shamelessly based on:
    http://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/
    """

    @staticmethod
    def get_plugins():
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
                if not os.path.isdir(location) or not "__init__.py" in os.listdir(location):
                    continue
                info = imp.find_module("__init__", [location])
                plugins[i] = ({"name": i, "info": info})
        return plugins

    @staticmethod
    def load_plugin(plugin_name):
        """ Load an individual plugin. """
        plugins = Plugin.get_plugins()
        try:
            plugin = plugins[plugin_name]
        except KeyError as error:
            try:
                plugin = Plugin.download_plugin(plugin_name)
            except DrupdatesError as error:
                msg = "Unable to find plugin {0}, ensure it exists".format(plugin_name)
                raise DrupdatesError(30, msg)
        return imp.load_module("__init__", *plugin["info"])

    @staticmethod
    def download_plugin(name):
        """ Download the plugin, name, Drupdates oragnization on Github. """
        uri = 'https://github.com/drupdates/' + name + '.git'
        plugins_dir = Utils.check_dir(os.path.join('~', '.drupdates', 'plugins'))
        if not bool(urlparse(uri).netloc):
            msg = ("Error: {0} url, {1}, is not a valid url").format(name, uri)
            raise DrupdatesError(20, msg)
        response = requests.get(uri)
        if response.status_code not in [200, 201]:
            msg = "Plugin url {0} returned an invalid HTTP response code {1}".format(uri, response.status_code)
            raise DrupdatesError(20, msg)
        try:
            Repo.clone_from(uri, os.path.join(plugins_dir, name.title()))
        except git.exc.GitCommandError as git_error:
            msg = "Failed to clone the plugin repo\n Error: {0}".format(git_error)
            raise DrupdatesError(20, msg)
        else:
            plugins = Plugin.get_plugins()
            return plugins[name]
