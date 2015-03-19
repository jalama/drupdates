""" Run Drush related commands. """
import subprocess
import json
import os
from drupdates.settings import Settings

class Drush(object):
    """ Base class to run Drush commands. """

    def __init__(self):
        self.settings = Settings()

    @staticmethod
    def call(commands, alias='', json_ret=False):
        """ Run a drush comand and return a list/dictionary of the results.

        Keyword arguments:
        commands -- list containing command, arguments and options
        alias -- drush site alias of site where "commands" to run on
        json -- binary deermining if the given command can/should return json

        """
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

    def db_import(self, alias):
        """ Import a SQL dump using drush sqlc.

        alias -- A Drush alias

        """
        backport_dir = self.settings.get('backupDir')
        if os.path.isfile(backport_dir + alias + '.sql'):
            commands = ['drush', '@drupdates.' + alias, 'sqlc']
            popen = subprocess.Popen(commands, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            results = popen.communicate(file(backport_dir + alias + '.sql').read())
            if results[1]:
                print "{0} DB import error: {1}".format(alias, results[1])
                return False
        else:
            print "{0} could not find backup file, skipping import".format(alias)
        return True
