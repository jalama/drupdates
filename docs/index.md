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

SQLite

Python versions: 2.6, 2.7, 3.3, 3.4

Installation
============
(sudo) pip install drupdates

Once installed please follow the post install [set-up instructions](setup.md)

Upgrade
============

pip --upgrade drupdates

Execution
============

$ drupdates

note: Any setting can be passed as an option from the CLI, so if you want
Drupdates to use /opt/ as the working directory in lieu of $HOME/.drupdates/builds

$ drupdates --workingDir=/opt/

Uninstall
============

(sudo) pip uninstall drupdates

Assumptions
===========

- Only tested on POSIX boxes, sorry no Windows yet.

- Drupdates is built assuming you can store passwords for 3rd party systems in
it's configuration files.  Drupdates will need to store system user names
and passwords in the $HOME/.drupdates directory.  This will mean that directory
 will need to be locked down.

- Any [Make](make.md) file used to build a site will be named the same as the site folder.

- Git is being used to track changes to the Drupal code base

Configuration
===========

Out of the box some basic configuration is in place but you will need to work
with the Drupdates [settings](settings.md) system to complete the set-up
to meet the needs of your Drupal site(s) and development system(s).

Please note out of the box the following settings are assumed:
- SQLite is the database storing your Drupal site
- Only Security updates are being run
- You Drupal sites are being installed at $HOME/.drupdates/builds
- sendmail will be used to email reports (other options are printing to the screen,
via stdout or sending to a Slack channel)
