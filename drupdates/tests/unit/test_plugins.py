""" Test Plugin functionality. """
import yaml, os, shutil
from os.path import expanduser
from drupdates.utils import Utils
from drupdates.plugins import Plugin
from drupdates.settings import DrupdatesError

class TestPlugins(object):
    """ Test a debug report file is output. """

    def setup(self):
        """ Setup the plugins directory. """
        Utils.check_dir(os.path.join(expanduser('~'), '.drupdates', 'plugins'))

    def teardown(self):
        """ Teardown the plugins directory. """
        folder = os.path.join(expanduser('~'), '.drupdates', 'plugins')
        if os.path.isdir(folder):
            shutil.rmtree(folder)

    def __init__(self):
        self.current_dir = os.path.dirname(os.path.realpath(__file__))

    def test_custom_plugin(self):
        """ Test loading a custom plugin called Druptest."""
        plugin_name = 'Druptest'
        source = os.path.join(self.current_dir, 'classes', plugin_name)
        target = os.path.join(expanduser('~'), '.drupdates', 'plugins', plugin_name)
        shutil.copytree(source, target)
        plugins = Plugin.get_plugins()
        assert plugins[plugin_name]['name'] == plugin_name

    def test_override_plugin(self):
        """ Test overriding the core Stdout plugin. """
        plugin_name = 'Stdout'
        source = os.path.join(self.current_dir, 'classes', plugin_name)
        target = os.path.join(expanduser('~'), '.drupdates', 'plugins', plugin_name)
        shutil.copytree(source, target)
        plugins = Plugin.get_plugins()
        assert plugins[plugin_name]['info'][1] == os.path.join(target, '__init__.py')


    def test_nonexistant_plugin(self):
        """ Test non-existant plugin. """
        plugin_name = 'Goblue'
        try:
            plugins = Plugin.load_plugin(plugin_name)
        except DrupdatesError as plugin_error:
            message = "Unable to find plugin '{0}', ensure it exists".format(plugin_name)
            assert plugin_error.msg == message
