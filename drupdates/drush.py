""" Run Drush related commands. """
import subprocess, json, copy
from drupdates.settings import Settings
from drupdates.settings import DrupdatesError

class DrupdatesDrushError(DrupdatesError):
    """ Parent Drupdates site build error. """

class Drush(object):
    """ Base class to run Drush commands. """

    def __init__(self):
        self.settings = Settings()

    @staticmethod
    def call(cmds, alias='', json_ret=False):
        """ Run a drush comand and return a list/dictionary of the results.

        Keyword arguments:
        commands -- list containing command, arguments and options
        alias -- drush site alias of site where "commands" to run on
        json -- binary deermining if the given command can/should return json

        """
        commands = copy.copy(cmds)
        if alias:
            commands.insert(0, '@drupdates.' + alias)
        if json_ret:
            commands.append('--format=json')
        commands.insert(0, 'drush')
        # run the command
        try:
            popen = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as error:
            msg = "Cannot run drush.call(),"
            msg += "most likely because Python can't find Drush\n Error: {0}".format(error.strerror)
            raise DrupdatesDrushError(30, msg)
        results = popen.communicate()
        if popen.returncode != 0:
            msg = "Drush.call() error, Drush command passed was {0}\n".format(commands)
            msg += "Drush error message: {0}".format(results[1])
            raise DrupdatesDrushError(20, msg)
        stdout = results[0]
        if json_ret:
            try:
                ret = json.loads(stdout.decode())
            except ValueError:
                msg = "{0}, No JSON returned from Drush, though it was requested\n".format(alias)
                msg += "Drush command passed was {0}\n".format(commands)
                msg += "Drush message: {0}".format(stdout)
                raise DrupdatesDrushError(20, msg)
        else:
            ret = stdout.decode().split('\n')
        return ret

    @staticmethod
    def get_sub_site_aliases(base_dir=None, system='drupdates'):
        aliases = {}
        drupdates_aliases = Drush.call(['sa', '@' + system, '--with-db'], '', True)
        for alias, data in drupdates_aliases.items():
            if base_dir and alias.split('.')[1] != base_dir:
                continue
            if data['uri'] != 'default' and data['uri'] != 'all':
                aliases[str(alias[10:])] = data
        return aliases
