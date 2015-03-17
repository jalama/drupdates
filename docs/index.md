Drupdates
===========
Script to maintain web sitescode bases, specifically Drupal, using [Drush](http://www.drush.org)

This script performs 4 major functions (ie phases):

1. Builds a site's directory from a Git repository.
2. Updates the site using drush pm-update, defaults to security update(s) only.
3. Submit a deployment ticket for the updated codebase.
4. Report on the site(s) Drupdates attempted to update.

Installation
============
easy_install https://github.com/jalama/drupdates/tarball/master

note: you may need sudo to run easy_install

Upgrade
============

easy_install --upgrade duprdates

Execution
============

$ drupdates

note: Any setting can be passed as an option from the CLI, so if you want
Drupdates to use /opt/ as the working directory in lieu of /var/www/

$ drupdates --workingDir=/opt/

Uninstall
============

(sudo) pip uninstall drupdates

Requirements
============
Drush 7

Git 1.7+

Assumptions
===========

- Only tested on POSIX boxes with Python 2.6 and 2.7, sorry no Windows yet.

- Python 3+ support is [forthcoming](https://github.com/jalama/drupdates/issues/15).

- Drupdates is not intended for production systems, it is built assuming it
will only be run on local development machines.  Drupdates will need to store
system user names and passwords in the $HOME/.drupdates directory.

- Drupdates does not support multi-site installs out of the box.

- The entire script depends on the use of Drush site aliases named after the
folders the sites are written to (prefixed with "drupdates".  Drupdates assumes
any back-up files follow the pattern of being named after that same
folder/<site alias>.
  - example: site folder is /var/www/drupal the back-up file is
<backports dir>/drupal.sql and the Drush alias will be @drupdates.drupal

- Lack of a back-up will not stop Drupdates from updating the Drupal codebase.

- Any [Make](make.md) file used to build a site will be named the same as the site folder.

Configuration
===========

Out of the box some basic configuration is in place but you will need to work
with the Drupdates [settings](settings.md) system to complete the set-up
to meet the needs of you Drupal site(s) and development system(s).

Please note out of the box the following settings are assumed:
- MYSQL is the database storing your Drupal site
- Only Security updates are being run
- You Drupal sites are being installed at /var/www
- sendmail wil be used to send reports

