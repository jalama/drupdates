""" Parent class for plugins that print Drupdates final report. """
from drupdates.settings import Settings
from drupdates.plugins import Plugin
import abc

class Reports(Plugin):
    """ Class for print reports. """

    def __init__(self):
        # load the Plugin _plugins property
        self.settings = Settings()
        tool = self.settings.get('reportingTool').title()
        self._plugin = Plugin.load_plugin(tool)
        class_ = getattr(self._plugin, tool)
        self._instance = class_()

    def json(self, report):
        import json
        return json.dumps(report)

    def yaml(self, report):
        import yaml
        return yaml.dump(report, default_flow_style=False)

    def text(self, report, text=""):
        """ Format the report dictionary into a string. """
        return self.yaml(report)

    def send(self, report):
        """ Deliver the report. """
        report_format = self.settings.get('reportingFormat')
        class_ = getattr(self, report_format)
        report_text = class_(report)
        return self._instance.send_message(report_text)

class Report(object):
    """ Abstract class for report Plugins. """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def send_message(self, report_text):
        """ Abstract method to send report. """
        pass
