""" Manage SQL database storage engines. """
from drupdates.settings import Settings
from drupdates.drush import Drush
from drupdates.constructors.datastores import Datastore
import os
from os.path import expanduser
from string import Template

class Sql(Datastore):
    """ SQL database plugin. """

    def __init__(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        settings_file = current_dir + '/settings/default.yaml'
        self.settings = Settings()
        self.settings.add(settings_file)
        self._alias_file = None

    @property
    def alias_file(self):
        """ alias_file getter. """
        return self._alias_file
    @alias_file.setter
    def alias_file(self, value):
        """ alias_file setter. """
        self._alias_file = value

    def write_my_cnf(self):
        """ Create a my.cnf file.

        If the mysql root password = "" we have to create this file for drush to
        run sql-create correctly.
        Without ~/.my.cnf file drush sql-create won't pass the --db-su option.

        """
        my_file = self.settings.get('mysqlSettingsFile')
        local_file = expanduser('~') + '/' + my_file
        ret = False
        if os.path.isfile(local_file):
            ret = True
        else:
            try:
                filepath = open(local_file, 'w')
            except IOError as error:
                print "Could not write the {0} file\n Error: {1}".format(local_file, error.strerror)
                return ret
            userline = "user = {0} \n".format(self.settings.get('datastoreSuperUser'))
            password = self.settings.get('datastoreSuperPword')
            settings = self.settings.get('mysqlSettings')
            filepath.write("#This file was written by the Drupdates script\n")
            for setting in settings:
                settingline = "[{0}]\n".format(setting)
                filepath.write(settingline)
                filepath.write(userline)
                if password:
                    passline = "password = {0} \n".format(password)
                    filepath.write(passline)
                filepath.write("\n")
            filepath.close()
            ret = True
        return ret

    def delete_files(self):
        """ Clean-up my.cnf file."""
        my_file = self.settings.get('mysqlSettingsFile')
        local_file = expanduser('~') + '/' + my_file
        if os.path.isfile(local_file):
            try:
                os.remove(local_file)
            except OSError as error:
                msg = "Clean-up error, couldn't remove {0}\n".format(local_file)
                msg += "Error: {1}".format(error.strerror)
                print msg
        if os.path.isfile(self.alias_file):
            try:
                os.remove(self.alias_file)
            except OSError as error:
                msg = "Clean-up error, couldn't remove {0}\n".format(self.alias_file)
                msg += "Error: {1}".format(error.strerror)
                print msg
        return True

    def create(self, site):
        """ Create a MYSQL Database."""
        driver = self.settings.get('datastoreDriver')
        spwd = self.settings.get('datastoreSuperPword')
        suser = self.settings.get('datastoreSuperUser')
        if driver == 'mysql' and not spwd:
            if not self.write_my_cnf():
                return False
        create_cmds = ['sql-create', '-y', '--db-su=' + suser, '--db-su-pw=' + spwd]
        Drush.call(create_cmds, site)
        return True

    def aliases(self):
        """ Build a Drush alias file in $HOME/.drush, with alises to be used later.

        Notes:
        The file name is controlled by the drushAliasFile settings
        All of the aliases will be prefixed with "drupdates" if he default file name
          is retained
        """

        ret = False
        alias_file_name = self.settings.get('drushAliasFile')
        drush_folder = expanduser('~') + '/.drush'
        self.alias_file = drush_folder + "/" + alias_file_name
        if not os.path.isdir(drush_folder):
            try:
                os.makedirs(drush_folder)
            except OSError as error:
                print "Could not create ~/.drush folder \n Error: {0}".format(error.strerror)
                return ret
        current_dir = os.path.dirname(os.path.realpath(__file__))
        # Symlink the Drush aliases file
        src = current_dir + "/templates/aliases.template"
        doc = open(src)
        template = Template(doc.read())
        doc.close()
        try:
            filepath = open(self.alias_file, 'w')
        except OSError as error:
            print "Could not create {0} folder\n Error: {1}".format(self.alias_file, error.strerror)
            return ret
        webroot_dir = self.settings.get('webrootDir')
        host_set = self.settings.get('datastoreHost')
        driver_set = self.settings.get('datastoreDriver')
        path_set = self.settings.get('workingDir')
        port_set = self.settings.get('datastorePort')
        filepath.write(template.safe_substitute(host=host_set, driver=driver_set,
                                                path=path_set, webroot=webroot_dir, port=port_set))
        filepath.close()
        ret = True
        return ret







