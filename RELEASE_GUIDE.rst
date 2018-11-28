
Release Workflow
=================
To perform a release follow the following steps

#. Run a `make clean`
#. Run a `make test-all` and ensure the library passes all tests
#. Run a `make dist` to create distrubtion egg
#. Run a `make release-staging`
#. Test the staging release works as expected
#. Run a `make release-production`

Setup
=======

You need to first setup pip to publish to stagin and production. To do this, edit
~/.pypirc to have the following contents. Replace the email and password


```
[distutils]
index-servers = production staging

[staging]
repository: https://packages.idmod.org/api/pypi/idm-pypi-staging
username: email
password: password

[production]
repository: https://packages.idmod.org/api/pypi/idm-pypi-production
username: email
password: password
````