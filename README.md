Drupdates
===========
Scripts to maintain web sites code bases, specifically Drupal sites using Drush

This script performs 4 major functions (ie phases):

1. Builds a site's directory from a Git repository.
2. Updates the site using drush pm-update, default to security update(s) only.
3. Submit a deployment ticket for the updated codebase.
4. Report on the site(s) Drupdates attempted to update.

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
Drush 7
Git 1.7+

Assumptions
===========

- Only tested on POSIX boxes with Python 2.6 and 2.7, sorry no Windows yet.

- Python 3+ support is forthcoming.

- Drupdates is not intended for production systems, it is built assuming it
will only be run on local development machines.  Drupdates will need to store
system user names and passwords in the $HOME/.drupdates directory.

- Drupdates does not support multi-site installs out of the box.

- The entire script depends on the use of Drush site aliases named after the
folders the sites are written to (prefixed with "drupdates".  Drupdates assumes
any back-up files follow the pattern of being named after that same
folder/<site alias>.
  - example: site folder is /var/www/drupal the back-up file is drupal.sql and
  the Drush alias will be drupdates.drupal

- Lack of a back-up will not stop Drupdates from updating the Drupal codebase.

- Any Make file used to build a site will be named the same as the site folder.

- By default the script tries to build the sites in /var/www/

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

Make File
===========

Make FIles can be used to build the site.  The following settings will be
required:

useMakeFile, needs to be set to a non "Falsey" value, ie "Yes".
webrootDir, needs to be set to a non "Falsey" value, ie webroot or html.

It's worth noting Drupdates can support two file structures with regards to
make files.  The setting that contorls this is "buildSource".

1. Ship only a make file that will later be used to build the site codebase.
  - buildSource: make
2. Ship the make file along with a complete codebase in a webroot sub-folder.
  - buildSource: git
  - example file structure:
    - drupal.make
    - webroot
      - <Drupal codebase>

