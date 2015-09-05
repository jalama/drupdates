""" Class to set-up the configuration used throughout Drupdates """
import os, yaml, sys, json, copy
from os.path import expanduser
try:
    import argparse
    ARG_LOADED = True
except ImportError:
    # Python 2.6
    from optparse import OptionParser
    ARG_LOADED = False

class DrupdatesError(Exception):
    """ Parent Drupdates error.

    level notes:

    Warning  =< 10
    Critical =< 20
    Fatal > 20

    """
    def __init__(self, level, msg):
        Exception.__init__(self)
        self.level = level
        self.msg = msg

class _Settings(object):
    """ Build the settings used throughout the drupdates project.

        Settings are built from either YAML files or options passed when run on
        CLI. Settings are loaded in this order:
        - Core settings file, ie drupdates/settings/default.yaml
        - Plugin settings files, ie <plugin dir>/settings/default.yaml
        - Local settings file in $HOME/.drupdates, ie $HOME/.drupdates/settings.yaml
        - Working Directory settings file, ie <working_directory>/.drupdates/settings.yaml
        - Site Repo settings file, ie <webroot>/.drupdates/settings.yaml
        - Options passed at runtime, ie $python -m drupdates --workingDir=/opt/
        - Prompts to end user, only if required and no value found above

        The later the setting is loaded the higher its weight, ie if it's set at
        runtime it will overwrite anything set in the Core or local settings file.

    """

    def __init__(self):
        self.settings = {}
        current_dir = os.path.dirname(os.path.realpath(__file__))
        settings_file = current_dir + '/settings/default.yaml'
        self.add(settings_file)
        self._custom_settings()
        self.core_settings = copy.copy(self.settings)
        self._options = self.options()

    def _custom_settings(self):
        """ Load custom settings file in $HOME/.drupdates/settings.yaml. """
        path = __name__
        local_file = expanduser('~') + '/.' + '/'.join(path.split('.')) + '.yaml'
        # If there is an override file in the home dir
        # (ex. ~/.drupdates/settings.yaml)
        try:
            self.add(local_file, True)
        except DrupdatesError:
            pass

    def options(self):
        """ Read the options set at runtime. """
        if ARG_LOADED:
            parser = argparse.ArgumentParser()
            model = self._model()
            for key, setting in self.settings.items():
                setting_complete = self.merge(model, setting)
                parser.add_argument("--" + key, dest=key,
                                    help=setting_complete['prompt'])
            options = parser.parse_args()
        else:
            parser = OptionParser()
            model = self._model()
            for key, setting in self.settings.items():
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
        self.set(setting, value, complete['format'])

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

    def add(self, settings_file, force=False):
        """ Load/Add settings from a YAML file.

        Keyword arguments:
        settings_file -- file path to a settings YAML file (required)
        force -- Incoming settings overwrite current settings (default = False)

        """
        try:
            default = open(settings_file, 'r')
        except IOError as error:
            msg = "Can't open or read settings file, {0}".format(settings_file)
            raise DrupdatesError(20, msg)
        new = yaml.load(default)
        default.close()
        for setting, item in new.items():
            if not isinstance(item, dict):
                error = "Exiting Drupdates \n"
                error += "Fatal Error: Settngs file, {0}, ".format(settings_file)
                error += "failed to load or parse properly. \n"
                error += "{0} setting is fomatted improperly".format(setting)
                sys.exit(error)
        if not force:
            self.settings = self.merge(new, self.settings)
        else:
            self.settings = self.merge(self.settings, new)
        self._options = self.options()

    def set(self, setting, value, setting_format='str'):
        """ Setter function for Settings class. """
        if setting_format:
            if setting_format == 'list':
                value = value.split()
            elif setting_format == 'dict':
                value = json.loads(value)
        self.settings[setting]['value'] = value

    def merge(self, target, source, path=None):
        """ Utiliity used to merge two dictionaries, merges source into target.

        If target and source contain same key, return will contain source value.
        """
        if path is None:
            path = []
        for key in source:
            if key in target:
                if isinstance(target[key], dict) and isinstance(source[key], dict) and key == 'value':
                    self.merge(target[key], source[key], path + [str(key)])
                else:
                    target[key] = source[key]
            else:
                target[key] = source[key]
        return target

    def reset(self):
        """ Reset the settings attribute. """
        self.settings = self.core_settings

    def list(self):
        """ Return settings list. """
        return self.settings

class Settings(object):
    """ Base Settings class. """

    instance = None
    def __new__(cls):
        if not Settings.instance:
            Settings.instance = _Settings()
        return Settings.instance

    @staticmethod
    def get(setting):
        """ Get the setting. """
        return Settings.instance.get(setting)

    @staticmethod
    def set(setting, value, setting_format=''):
        """ Set the setting. """
        return Settings.instance.set(setting, value, setting_format)

    @staticmethod
    def add(settings_file, force=False):
        """ Load settings from a YAML file. """
        return Settings.instance.add(settings_file, force)

    @staticmethod
    def reset():
        """ Reset the settings. """
        Settings.instance.reset()

    @staticmethod
    def list():
        """ Provide dictionary of all the settings. """
        return Settings.instance.list()
