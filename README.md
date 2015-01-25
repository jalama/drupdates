Drupdates
===========
Scripts to maintain web sites code bases, specifically Drupal sites using Drush

This script performs 4 major functions (ie phases):

1.) Builds a site's directory from a Git repository.
2.) Updates the site using drush pm-update, default to security update(s) only.
3.) Submit a deployment ticket for the updated codebase.
4.) Report on the site(s) Drupdates attempted to update.

Installation
============
easy_install https://github.com/jalama/drupdates/tarball/master

note: you may need sudo to run easy_install

Execution
============

$ drupdates

note: Any setting can be passed as an option from the CLI, so if you want
Drupdates to use /opt/ as the working directory in lieu of /var/www/

$ drupdates --workingDir=/opt/

Requirements
============
Drush (preferably Drush 7)
Git 1.7+

Assumptions
===========

- Only tested on POSIX boxes with Python 2.6 and 2.7, sorry no Windows yet.

- Python 3+ support is forthcoming.

- Drupdates is not intened for production systems, it is built assuming it
will only be run on local development machines.  Drupdates will need to store
system user names and passwords in the $HOME/.drupdates directory.

- The entire script depends on the use of Drush site aliases named after the
folders the sites are written to (prefixed with "drupdates".  Drupdates assumes
any back-up files follow the pattern of being named after that same
folder/<site alias>.
  - example: site folder is /var/www/drupal the back-up file is drupal.sql and
  the Drush alias will be drupdates.drupal

- By default the script tries to build the sites in /var/www/

Settings
===========

To make this script meet your needs you will need to customize the settings,
loaded from YAML files.  As of version 1.0 there is no installer so the settings
are changed and updated by either using a YAML file or passing options at
runtime.

At see http://pyyaml.org/wiki/PyYAMLDocumentation for YAML basics.

Here's how it works:

Settings are built from either YAML files or options passed when run on CLI.
- Settings are loaded in this order:
  - Core settings file, ie drupdates/settings/default.yaml
  - Plugin settings files, ie <plugin dir>/settings/default.yaml
  - Local settings file in $HOME/.drupdates, ie $HOME/.drupdates/settings.py
  - Options passed at runtime, ie $python -m drupdates --workingDir=/opt/
  - Prompts to end user, only if required and not value found above

Settings loaded later take precident over the same setting loaded earlier,
ie if it's set at runtime it will overwrite anything set in the Core settings
or local settings files.

The Core settings file is <module dir>/drupdates/settings/default.yaml or
https://github.com/jalama/drupdates/blob/master/drupdates/settings/default.yaml.
Additionally, each plugin ships with it's own default.yaml file in its
respective settings directory.

Settings Format:

Each setting in the YAML file needs to look like this or it will be assumed
to be blank (ie "").  <notes on what each line means for clarities sake>

setting:  <the name of the setting>
  value: <required, value of the setting*>

Optionally each setting can have other attributes (@see Settings.model()):

setting:
  value:
  prompt: <optionsl, Prompt presented at runtime if setting is null and required>
  format: <optionsl, What is the format, supported values: string (default), list, dict>
  required: <optionsl, Is the setting required**>

* Surround with '' if value contains special cahracters.  For list of YAML
special characters @see http://www.yaml.org/refcard.html.
** If setting is required and is empty, the end user will be asked for a value.

Plugins
===========

There is a realtively primitive Plugin system based om a set of "constructor"
classes that load the appropriate child class(s).

In version 1.0 there are 4 sets of plugin types:

- Git Repo lists (think Stash)
- Project management tools (think AtTask, JIRA, etc...)
- Datastores (currently only sql)*
- Report delivery methods (ie e-mail, IM, etc...)

The plugins can be found in the <module dir>/drupdates/plugins folder with their
respective consturctors in <module dir>/drupdates/constructors.  With version
1.0 all of the constructors define abstract classes used by the individual
plugins.

* We shamelessly punt management of the sql to Drush, so in theory Drupdates
supports anything Drush does, though only mysql has been tested at as of v1.1.

