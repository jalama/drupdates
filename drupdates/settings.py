import os, yaml
from drupdates.utils import *
from os.path import expanduser
try:
  import argparse
  arg_loaded = True
except ImportError:
  from optparse import OptionParser
  arg_loaded = False

class Settings(object):

  def __init__(self, currentDir = ""):
    if not currentDir:
      currentDir = os.path.dirname(os.path.realpath(__file__))
    self._settings = currentDir
    self._model = {}
    self.options()

  @property
  def _settings(self):
      return self.__settings
  @_settings.setter
  def _settings(self, currentDir):
    """ Build the settings used through the drupdates project.

    Settings are built from either YAML files or options passed when run on CLI.
    Settings are loaded in this order:
    - Core settings file, ie drupdates/settings/default.yaml
    - Plugin settings files, ie <plugin dir>/settings/default.yaml
    - Local settings file in $HOME/.drupdates, ie $HOME/.drupdates/settings.py
    - Options passed at runtime, ie $python -m drupdates --workingDir=/opt/
    - Prompts to end user, only if required and not value found above

    The later the setting is loaded the higher it's weight, ie if it's set at
    at runtime it will overwrite anything set in the Core settings or local
    settings file.

    """
    self.__settings = {}
    packageDefaultYaml = os.path.dirname(os.path.realpath(__file__))
    packageDefault = open(packageDefaultYaml + '/settings/default.yaml', 'r')
    self.__settings =  yaml.load(packageDefault)
    packageDefault.close()
    ## this will load a Plugins default settings
    if not packageDefaultYaml == currentDir:
      default = open(currentDir + '/settings/default.yaml', 'r')
      self.__plugin =  yaml.load(default)
      default.close()
      self.__settings = self.merge(self.__settings, self.__plugin)
    path = __name__
    localFile = expanduser('~') + '/.' + '/'.join(path.split('.')) + '.yaml'
    # If there is an override file in the home dir (ex. ~/.drupdates/settings.yaml)
    if os.path.isfile(localFile):
      local = open(localFile, 'r')
      self.__local =  yaml.load(local)
      local.close()
      self.__settings = self.merge(self.__settings, self.__local)

  def options(self):
    """ Read the options set at runtime. """
    # FIXME: add support for type validation
    # @see https://docs.python.org/2/library/optparse.html#optparse.Option.type
    if arg_loaded:
      parser = argparse.ArgumentParser()
      for key, setting in self._settings.iteritems():
        settingComplete = self.merge(self._model, setting)
        parser.add_argument("--" + key, dest=key,
                          default=settingComplete['value'],
                          help=settingComplete['prompt'])
      options = parser.parse_args()
    else:
      parser = OptionParser()
      for key, setting in self._settings.iteritems():
        settingComplete = self.merge(self._model, setting)
        parser.add_option("--" + key, action="store", dest=key,
                          default=settingComplete['value'],
                          type="string", help=settingComplete['prompt'])
      (options, args) = parser.parse_args()
    self.__options = options

  @property
  def _model(self):
      return self.__model
  @_model.setter
  def _model(self, value = {}):
    value['default'] = ''
    value['value'] = ''
    value['prompt'] = ''
    value['format'] = ''
    value['required'] = ''
    self.__model = value

  def get(self, setting):
    if setting in self._settings:
      settingComplete = self.merge(self._model, self._settings[setting])
      settingComplete['value'] = getattr(self.__options, setting)
      if not settingComplete['value'] and settingComplete['required']:
        value = raw_input(settingComplete['prompt'] + ":")
        self.set(setting, value, settingComplete)
      return settingComplete['value']
    else:
      return ""

  def set(self, setting, value, complete):
    # FIXME: need better format parsing (ie int, boolean, dict, list etc...)
    if complete['format'] == 'list':
      value = value.split()
    elif complete['format'] == 'dict':
      import json
      value = json.loads(value)
    self.__settings[setting]['value'] = value

  def merge(self, a, b, path=None):
    """Utiliity used to merge two dictionaries, merges b into a. """
    if path is None: path = []
    for key in b:
      if key in a:
        if isinstance(a[key], dict) and isinstance(b[key], dict):
          self.merge(a[key], b[key], path + [str(key)])
        else:
          a[key] = b[key]
      else:
        a[key] = b[key]
    return a
