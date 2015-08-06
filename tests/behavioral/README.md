
Build out repos for test to run against along with the settings files needed.

Add the settings for the test to the /tests/behavioral/settings folder as .yaml files

Naming conventions:

- Test class file start with the name "test_"
    - ex. "test_multiple_sites.py"
- Settings files are the name of the test class file above without the "test_" prefix
    - ex. settings/multiple_sites.yaml

Sample values:
repo_dirs:
   example: # test install folder name
     working_directory: # base test dir will be prepended, defaults to builds
     custom_settings: # .yaml extension added, file placed in working_directory .drupdates folder
     base: # base repo the test repo is built from
 options: # options passed to drupdates cli call
   singleSite: drupal # example of passing the SingleSite setting for repo_dir name drupal.
 settings_file: drupal # .yaml extension added, consider inserting settings below.

 If you are testing locally, move to the drupdates folder and run nosetests:

 ```
 nosetests
 ```

 To run an individual test from the drupdates folder:
 ex: the test in the <drupdates folder>/tests/behavioral/test_multiple_sites.py
 ```
nosetests tests.behavioral.test_multiple_sites
```

If you have print statements in the tests, for debugging
ex: the test in the <drupdates folder>/tests/behavioral/test_multiple_sites.py
```
nosetests --nocapture tests.behavioral.test_multiple_sites
```
