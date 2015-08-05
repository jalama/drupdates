Drupdates
===========
Script to maintain web sitescode bases, specifically Drupal, using [Drush](http://www.drush.org)

This script performs 4 major functions (ie phases):

1. Builds a site's directory from a Git repository.
2. Updates the site using drush pm-update, defaults to security update(s) only.
3. Submit a deployment ticket for the updated codebase.
4. Report on the site(s) Drupdates attempted to update.


System Requirements
============
Drush 7

Git 1.7+

Installation
============
(sudo) pip install https://github.com/jalama/drupdates/tarball/master

Once installed please follow the post install [set-up instructions](setup.md)

Upgrade
============

pip --upgrade drupdates

Execution
============

$ drupdates

note: Any setting can be passed as an option from the CLI, so if you want
Drupdates to use /opt/ as the working directory in lieu of /var/www/

$ drupdates --workingDir=/opt/

Uninstall
============

(sudo) pip uninstall drupdates

Assumptions
===========

- Only tested on POSIX boxes with Python 2.6 and 2.7, sorry no Windows yet.

- Python 3+ support is [forthcoming](https://github.com/jalama/drupdates/issues/15).

- Drupdates is not intended for production systems, it is built assuming it
will only be run on local development machines.  Drupdates will need to store
system user names and passwords in the $HOME/.drupdates directory.

- Drupdates does not support Drupal's multi-site installs out of the box.

- Any [Make](make.md) file used to build a site will be named the same as the site folder.

- Git is being used to track changes to the Drupal code base

Configuration
===========

Out of the box some basic configuration is in place but you will need to work
with the Drupdates [settings](settings.md) system to complete the set-up
to meet the needs of you Drupal site(s) and development system(s).

Please note out of the box the following settings are assumed:
- SQLite is the database storing your Drupal site
- Only Security updates are being run
- You Drupal sites are being installed at /var/www
- sendmail will be used to send reports (other options are printing to the screen,
via stdout or sending to a Slack channel)
