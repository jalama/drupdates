Plugins
===========

There is a relatively primitive Plugin system based on a set of "constructor" classes that load the appropriate child class(s).

In version 1.3+ there are 3 sets of plugin types, aka constructors:

- Git Repo lists (think Stash)
- Project management tools (think AtTask, Jira, etc...)
- Report delivery methods (ie e-mail, IM, etc...)

The plugins can be found in the <module dir>/drupdates/plugins folder with their respective constructors in <module dir>/drupdates/constructors.  With version 1.0+ all of the constructors define abstract classes used by the individual plugins.

As of 1.5.0 custom Plugins can be added in the $HOME/.drupdates/plugins folder, in their own folder.  Each plugin must be based on an available an constructor (Pmtools, Reports or Repos) and ship with a __init__.py file in the root folder.  Additionally plugins can define their own [settings](settings.md) file in a settings/default.yaml file within it's plugin folder.

Sample folder structure:

```
    - __init_.py
    - settings
    -- default.yaml
```

Others can be seen in the [code base](../drupdates/plugins)

Drupdates only ships with a limited number of Plugins to get you started.  As of version 1.5.0 plugins that ship with Drupdates are limited by the following rules.

- They are freely available.
- They are embedded in the OS (ie don't require calls to 3rd party APIs).

Additional plugins that can be found in the [Drupdates Organization repositories](https://github.com/drupdates/) and can be downloaded by simply adding their name to you settings file.  Drupdates will scan the available Plugins and attempt to download the correct one into the $HOME/.drupdates/plugins folder.  Feel free to create new ones, we'll be happy to create repos for you on Github.
