How to set-up Behavioral tests:

Build out repos for test to run against along with the settings files. Add the
settings for the test to the /tests/behavioral/settings folder as .yaml files.
Tests are built and run in ~/.drupdates/testing by default.

Test and settings file naming conventions:

- Test class file start with the name "test_"
    - ex. "test_multiple_sites.py"
- Settings files are the name of the test class file above without the "test_" prefix
    - ex. settings/multiple_sites.yaml

Sample Test settings file:
```
Sample values:
working_dirs:
  builds:
    dir: builds
  test:
    dir:builds/test
    custom_settings:
repo_dirs:
  example: # test install folder name
    working_directory: builds # base test dir will be prepended, defaults to builds
    base: # base repo the test repo is built from
  example2:
    working_directory: test
    base:
    skip: True # Skip Adding this repo to the main settings.yaml file
options: # options passed to drupdates cli call
  singleSite: example # example of passing the SingleSite setting for repo_dir name example.
additional_settings: # Any additional setting not covered above to be inserted in the ~/.drupdates/settings.yaml file
```

If you are developing against source code and have Drupdates source code on your
 local machine, move to the drupdates folder and run nosetests:

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
