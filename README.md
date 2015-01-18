Drupdates
===========
Scripts to maintain web sites code bases, specifically Drupal sites using Drush

This script performs 4 major functions (ie phases):

1.) Builds a site's directory form a Git repository.
2.) Updates the site using drush pm-update, default to security update only.
3.) Will Submit a deployment ticket for the updated codebase.
4.) Report on the site(s) it attempted to update.

Installation
============
pip install git+git://github.com/jalama/drupdates.git

or

pip install git+https://github.com/jalama/drupdates.git

Execution
============

$ python -m drupdates

note: Any setting can be passed as an option form the CLI, so if you want drupdates
to use /opt/ as the working directory in lieu of /var/www/

$ python -m drupdates --workingDir=/opt/

Requirements
============
Drush (preferably Drush 7)
Git 1.7+
sendmail (there is an issue filed for SMTP support)

Assumptions
===========

- Only tested on Nix boxes using Python 2.6 and 2.7, sorry haven't testing on Windows

- Python 3+ support is forthcoming

- This is not a production ready system, it is inherently built assuming it
will only be run on local development machines, it will need to store system
password in file locally

- The entire script depends on the use of Drush site aliases names after the
folders the siters are written to.  The sites assumes any back files follow the
pattern of being named after that same folder/site alias.
  - example: site folder is drupal the back-up file is drupal.sql

- by default the script tries to build the sites in /var/www


