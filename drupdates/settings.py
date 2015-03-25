""" Class to set-up the configuration used throughout Drupdates """
import os, yaml, sys, json, os, yaml
from os.path import expanduser
try:
    import argparse
    ARG_LOADED = True
except ImportError:
    # Python 2.6
    from optparse import OptionParser
    ARG_LOADED = False

class Settings(object):
    """ Base Settings class """
    def __init__(self, current_dir=""):
        if not current_dir:
            current_dir = os.path.dirname(os.path.realpath(__file__))
        self.settings = self._settings(current_dir)
        self._options = self.options()

    def _settings(self, current_dir):
        """ Build the settings used through the drupdates project.

        Settings are built from either YAML files or options passed when run on CLI.
        Settings are loaded in this order:
        - Core settings file, ie drupdates/settings/default.yaml
        - Plugin settings files, ie <plugin dir>/settings/default.yaml
        - Local settings file in $HOME/.drupdates, ie $HOME/.drupdates/settings.py
        - Options passed at runtime, ie $python -m drupdates --workingDir=/opt/
        - Prompts to end user, only if required and not value found above

        The later the setting is loaded the higher its weight, ie if it's set at
        runtime it will overwrite anything set in the Core settings or local
        settings file.

        """
        settings = {}
        package_default_yaml = os.path.dirname(os.path.realpath(__file__))
        package_default = open(package_default_yaml + '/settings/default.yaml', 'r')
        settings = yaml.load(package_default)
        package_default.close()
        ## this will load a Plugins default settings
        if not package_default_yaml == current_dir:
            default = open(current_dir + '/settings/default.yaml', 'r')
            __plugin = yaml.load(default)
            default.close()
            settings = self.merge(settings, __plugin)
        path = __name__
        local_file = expanduser('~') + '/.' + '/'.join(path.split('.')) + '.yaml'
        # If there is an override file in the home dir
        # (ex. ~/.drupdates/settings.yaml)
        if os.path.isfile(local_file):
            local = open(local_file, 'r')
            __local = yaml.load(local)
            local.close()
            for setting, item in __local.iteritems():
                if not isinstance(item, dict):
                    error = "Exiting Drupdates \n"
                    error += "Fatal Error: Custom settngs file, {0}, ".format(local_file)
                    error += "failed to load or parse properly. \n"
                    error += "{0} setting is fomatted improperly".format(setting)
                    sys.exit(error)
            settings = self.merge(settings, __local)
        else:
            print "Exiting Drupdates, Local settings file, {0}, does not exist".format(local_file)
            sys.exit(1)
        return settings

    def options(self):
        """ Read the options set at runtime. """
        if ARG_LOADED:
            parser = argparse.ArgumentParser()
            model = self._model()
            for key, setting in self.settings.iteritems():
                setting_complete = self.merge(model, setting)
                parser.add_argument("--" + key, dest=key,
                                    help=setting_complete['prompt'])
            options = parser.parse_args()
        else:
            parser = OptionParser()
            model = self._model()
            for key, setting in self.settings.iteritems():
                setting_complete = self.merge(model, setting)
                parser.add_option("--" + key, action="store", dest=key, type="string",
                                  help=setting_complete['prompt'])
            parsed_options = parser.parse_args()
            options = parsed_options[0]
        return options

    @staticmethod
    def _model():
        """ Model for an individual setting. """
        value = {}
        value['value'] = ''
        value['prompt'] = ''
        value['format'] = ''
        value['required'] = ''
        # Does this setting require another setting be set
        value['requires'] = ''
        return value

    def query_user(self, setting, complete):
        """ Query the user for a partiular setting. """
        prompt = "Please provide the setting, {0}, {1}:".format(setting, complete['prompt'])
        value = raw_input(prompt)
        self.set(setting, value, complete)

    def get(self, setting):
        """ Getter for Settings class """
        if setting in self.settings:
            model = self._model()
            setting_complete = self.merge(model, self.settings[setting])
            cli_option = getattr(self._options, setting)
            if cli_option:
                setting_complete['value'] = cli_option
            if not setting_complete['value'] and setting_complete['required']:
                self.query_user(setting, setting_complete)
            if setting_complete['value'] and setting_complete['requires']:
                required = self.get(setting_complete['requires'])
                if not required:
                    self.query_user(setting_complete['requires'],
                                    self.settings[setting_complete['requires']])
            return setting_complete['value']
        else:
            return ""

    def set(self, setting, value, complete):
        """ Setter function for Settings class. """
        if 'format' in complete:
            if complete['format'] == 'list':
                value = value.split()
            elif complete['format'] == 'dict':
                value = json.loads(value)
        self.settings[setting]['value'] = value

    def merge(self, target, source, path=None):
        """ Utiliity used to merge two dictionaries, merges source into target. """
        if path is None:
            path = []
        for key in source:
            if key in target:
                if isinstance(target[key], dict) and isinstance(source[key], dict):
                    self.merge(target[key], source[key], path + [str(key)])
                else:
                    target[key] = source[key]
            else:
                target[key] = source[key]
        return target
