Settings
===========

To make this script meet your needs you will need to customize the settings,
loaded from YAML files.  As of version 1.0 there is no installer so the settings
are changed and updated by either using a YAML file or passing options at
runtime.

At see http://pyyaml.org/wiki/PyYAMLDocumentation for YAML basics.

Here's how it works:

Settings are built from either YAML files or options passed when run on CLI.

-  Settings are loaded in this order:
  -  Core settings file, ie drupdates/settings/default.yaml
  -  Plugin settings files, ie *plugin dir*/settings/default.yaml
  -  Local settings file in $HOME/.drupdates, ie $HOME/.drupdates/settings.py
  -  Options passed at runtime, ie $python -m drupdates --workingDir=/opt/
  -  Prompts to end user, only if required and not value found above

Settings loaded later take precident over the same setting loaded earlier,
ie if it's set at runtime it will overwrite anything set in the Core settings
or local settings files.

The Core settings file is /drupdates/settings/default.yaml or
https://github.com/jalama/drupdates/blob/master/drupdates/settings/default.yaml.
Additionally, each plugin ships with it's own default.yaml file in its
respective settings directory.

Settings Format:

Each setting in the YAML file needs to be a dictionary with the following keys.
Each setting should formatted like below or it will be assumed to be blank
(ie "") there are notes on what each line means for clarities sake.

```
setting: the name of the setting
  value: required, value of the setting1
```
Optionally each setting can have other attributes (@see Settings.model()):
```
setting:
  value:
  prompt: optional, Prompt presented at runtime if setting is null and required
  format: optional, What is the format, supported values: string (default), list, dict
  required: optional, Is the setting required2
  requires: optional, does this setting require another setting
```
1 Surround with '' if value contains special cahracters.  For list of YAML
special characters @see http://www.yaml.org/refcard.html.
2 If setting is required and is empty, the end user will be asked for a value.

**Sample Files:**
=================

- *Basic Settings:* use a manual repo list, submit deployment ticket to AtTask,
print report to the terminal screen, use MYSQL, MYSQL root user/password = root:
  - https://gist.github.com/jalama/c14c3e8880f7274dbb90

- *Basic Make file settings:* use a make file to build the site,
manual repo list, submit a deployment ticket to AtTask,
print report to the terminal screen, use MYSQL, MYSQL root user/password = root:
  - https://gist.github.com/jalama/28aee650f3250cf92a55

- *Basic Make file and full repo:*  Use a make file to build the site and ship
with the complete repo, manual repo list, submit deployment ticket to AtTask,
print report to the terminal screen, use MYSQL, MYSQL root user/password = root:
  - https://gist.github.com/jalama/29091db65a263ec021af

- *Using Stash/Slack*: Repo list in Stash user forks, Slack for reporting,
use a make file and ship with complete repo, submit deployment ticket to AtTask,
print report to the terminal screen, use MYSQL, MYSQL root user/password = root:
  - https://gist.github.com/jalama/6798bf4e1b8e28a31088
