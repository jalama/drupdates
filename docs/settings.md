Settings
===========

To make this script meet your needs you will need to customize the settings, loaded from YAML files.  As of version 1.0 there is no installer so the settings are changed and updated by either using a YAML file or passing options at runtime.

At see http://pyyaml.org/wiki/PyYAMLDocumentation for YAML basics.

Here's how it works:

Settings are built from either YAML files or options passed when run on CLI.

-  Settings are loaded in this order:<a name="overrides"></a>
    -  Core settings file, ie drupdates/settings/default.yaml
    -  [Plugin](plugins.md) settings files, ie *plugin dir*/settings/default.yaml
    -  Local settings file in $HOME/.drupdates, ie $HOME/.drupdates/settings.yaml
    -  Local settings file in a working directory, ie <working directory>/.drupdates/settings.yaml
    -  Local settings file in a Site Repo, ie <webroot>/.drupdates/settings.yaml
    -  Options passed at runtime, ie $python -m drupdates --workingDir=/opt/
    -  Prompts to end user, only if required and not value found above

Settings loaded later take precident over the same setting loaded earlier, i.e. if it's set at runtime it will overwrite anything set in the Core settings or local settings files.

The Core settings file is [/drupdates/settings/default.yaml](https://github.com/jalama/drupdates/blob/master/drupdates/settings default.yaml). Additionally, each plugin ships with it's own default.yaml file in its respective settings directory.

**Custom Settings file:**<a name="custom_settings"></a>

You will need to overwirte settings file upon set-up.  To do this create a local settings file in $HOME/.drupdates/settings.yaml.  Sample settings files can be found below.

Settings Format:

Each setting in the YAML file needs to be a dictionary with the following keys. Each setting should formatted like below or it will be assumed to be blank (ie "") there are notes on what each line means for clarities sake.

Note: Python interprets "" as False.

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

1 Surround with '' if value contains special cahracters.  For list of YAML special characters @see http://www.yaml.org/refcard.html.

2 If setting is required and is empty, the end user will be asked for a value.

**Sample Files:**<a name="samples"></a>
===========
- *Simpliest Settings file* use a manual repository list, work from the "dev" branch, print report to the terminal screen:
    - [Simple Settings Gist](https://gist.github.com/jalama/f76dc5647f3406229b94)

- *Basic Settings:* use a manual repo list, submit deployment ticket to AtTask, print report to the terminal screen:
    - [Basic Settings Gist](https://gist.github.com/jalama/c14c3e8880f7274dbb90)

- *Basic Make file Settings:* use a make file to build the site,
manual repo list, submit a deployment ticket to AtTask,
print report to the terminal screen:
    - [Basic Make file Settings Gist](https://gist.github.com/jalama/28aee650f3250cf92a55)

- *Basic Make file and full repo:*  Use a make file to build the site and ship
with the complete repo, manual repo list, submit deployment ticket to AtTask,
print report to the terminal screen:
    - [Basic Make file and full repo Gist](https://gist.github.com/jalama/29091db65a263ec021af)

- *Using Stash/Slack*: Repo list in Stash user forks, Slack for reporting,
use a make file and ship with complete repo, submit deployment ticket to AtTask,
print report to the terminal screen,
will run only on www.example.com:
    - [Using Stash/Slack Gist](https://gist.github.com/jalama/6798bf4e1b8e28a31088)

Working Directories
===========

Drupdates builds and edits Drupal sites in what is known as the "Working Directory", which is controlled by the workingDir settting.  The default working directory setting is:

```
~/.drupdates/builds
```

As with any setting this can be overridden in the custom settings file.  Further, there are special qualities to note about the working directories.

- You can run Drupdates on only one site in a working directory using the singleSite setting. For exampple, say you have the following setting for repoDict (short for Repository Dictionary)

```
repoDict:
  value:
    - drupal:ssh://git@example.com:sites/drupal
    - drupal_two: ssh://git@example.com:sites/drupal_two
```

If you only wanted to run Drupdates on the "drupal" site above you would pass the following
on the comand line.

```
$drupdates --singleSite=drupal
```

OR set the following in the $HOME/.drupdates/settings.yaml file.

```
singleSite:
  value: drupal
```

Multiple Working Directories
===========

- If you are maintaining sites with diffrent configurations, examples include:
  - Some use JIRA and others use AtTask
  - Some ship with make files and other don't etc...

You can have multiple working directories, each with it's own individual custom settings.  The individual working directories would need to have a .drupdates folder with a settings.yaml file.

For example, if you have a working directory at /var/www and /opt/builds each with it's own settings
the file structure would look like this:

```
$HOME/.drupdates/settings.yaml
/var/www/.drupdates/settings.yaml
/opt/builds/.drupdates/settings/yaml
```

The working directories only have to have setting relevant to those directories in their respective
 .drupdates directory

Note: you still need the default custom settings file at $HOME/.drupdates/settings.yaml, mainly becuase
this is where you set you working directories.  
