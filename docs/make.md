Make File
===========

Make Files can be used to build the site.  The following settings will be
required:

- useMakeFile, needs to be set to a non "Falsey" value, ie "Yes".
- webrootDir, needs to be set to a non "Falsey" value, ie webroot or html.

It's worth noting Drupdates can support two file structures with regards to make files.  The setting that controls this is "buildSource".

1. Ship only a make file that will later be used to build the site codebase.

  - buildSource: make

2. Ship the make file along with a complete codebase in a webroot sub-folder.

  - buildSource: git

Example: file structure (webrootDir setting set to "webroot"):

```
    - drupal.make
    - webroot
    -- <Drupal Codebase>
```
  Example: file structure (uses makeFolder setting set to "makesfiles"):

```
    - makefiles
    -- drupal.make
    - webroot
    -- <Drupal Codebase>
```

It's worth noting the later format is supported as some site maintainers may want to use Make files to maintain a site "Manifest" while at the same time have sites structures that cannot be built using Make files.  In particular sites that have symlinks, say to a common mounted media folder. ;)

As of Drush 7 makes files can be in either the traditional "INI" format or YAML, more documentation is provided on [drush.org](http://www.drush.org/en/master/make/#the-make-file-format).
