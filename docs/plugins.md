Plugins
===========

There is a realtively primitive Plugin system based om a set of "constructor" classes that load the appropriate child class(s).

In version 1.3+ there are 3 sets of plugin types:

- Git Repo lists (think Stash)
- Project management tools (think AtTask, JIRA, etc...)
- Report delivery methods (ie e-mail, IM, etc...)

The plugins can be found in the <module dir>/drupdates/plugins folder with their respective consturctors in <module dir>/drupdates/constructors.  With version 1.0 all of the constructors define abstract classes used by the individual plugins.
