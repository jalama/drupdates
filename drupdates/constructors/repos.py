""" Parent class for plugins that create Git repository list. """
from drupdates.settings import Settings
from drupdates.plugins import Plugin
import abc

class Repos(Plugin):
    """ Build Git repository list. """

    def __init__(self):
        # load the Plugin _plugins property
        self.settings = Settings()
        tool = self.settings.get('gitRepoName').title()
        self._plugin = Plugin.load_plugin(tool)
        class_ = getattr(self._plugin, tool)
        self._instance = class_()

    def get(self):
        """ Get repository list from plugin. """
        return self._instance.git_repos()

class Repotool(object):
    """ Abstract class for repo list plugins. """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def git_repos(self):
        """ Abstract Method to get repo list. """
        pass
