Drupdates
===========
Script to maintain Drupal web site(s) code base using [Drush](http://www.drush.org)

This script performs 4 major functions (ie phases):

1. Builds a site's directory from a Git repository.
2. Updates the site using drush pm-update, defaults to security update(s) only.
3. Submit a deployment ticket for the updated codebase.
4. Report on the site(s) Drupdates attempted to update.

Usage
============

See the [documentation](docs/index.md) for installation and set-up instructions.

Basic Requirements
============
[Drush](http://drush.org) 7 (requires composer)

Git 1.7+

SQLite

Assumptions
===========

- Only tested on POSIX boxes with Python 2.6 and 2.7, sorry no Windows yet.

- Python 3+ support is [forthcoming](https://github.com/jalama/drupdates/issues/15).

- Drupdates is not intended for production systems, it is built assuming it
will only be run on local development machines.  Drupdates will need to store
system user names and passwords in the $HOME/.drupdates directory.

- Drupdates does not support Drupal's multi-site installs out of the box.

- Any [Make](docs/make.md) file used to build a site will be named the same as the site folder.

- Git is being used to track changes to the Drupal code base

