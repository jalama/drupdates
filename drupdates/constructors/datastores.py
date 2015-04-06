""" Parent class for plugins that work with various data storage engines. """
from drupdates.settings import Settings
from drupdates.plugins import Plugin
import abc

class Datastores(Plugin):
    """ Work with various data storage engines. """

    def __init__(self):
        # load the Plugin _plugins property
        Plugin.__init__(self)
        plugins = self._plugins
        self.settings = Settings()
        tool = self.settings.get('datastore').title()
        self._plugin = self.load_plugin(plugins[tool])
        class_ = getattr(self._plugin, tool)
        self._instance = class_()

    def build(self, site):
        """ Build a database etc... """
        return self._instance.create(site)

    def create_alises(self, working_dir):
        """ Create an alias file. """
        return self._instance.aliases(working_dir)

    def clean_files(self):
        """ Clean up any files used by sotrage engine. """
        return self._instance.delete_files()

class Datastore(object):
    """ Abstract class for data storage engines. """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create(self, site):
        """ Abstract method for creating database or collection. """
        pass

    @abc.abstractmethod
    def aliases(self, working_dir):
        """ Abstract method for creating alias files. """
        pass

    @abc.abstractmethod
    def delete_files(self):
        """ Abstract class for file cleanup. """
        pass

