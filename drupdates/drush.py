""" Run Drush related commands. """
import subprocess, json, os, copy
from drupdates.settings import Settings

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
            msg += "most likely because python can't find drush\n Error: {0}".format(error.strerror)
            print msg
        results = popen.communicate()
        stdout = results[0]
        if json_ret:
            try:
                ret = json.loads(stdout)
            except ValueError:
                ret = "For {0}, No JSON returned for status, though it was requested".format(alias)
        else:
            ret = stdout.split('\n')
        return ret
