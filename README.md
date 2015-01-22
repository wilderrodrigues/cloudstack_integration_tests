cloudstack_integration_tests
============================

This repository is intended keep my Aapache CloudStack integration tests, Marvin setup, and other utilities

== Deploy Datacenter

python deployDataCenter.py -i /Users/wrodrigues/sbp_dev/cloudstack_integration_tests/cit/integration/acs/config/devcloud-advanced.cfg

== Run tests

nosetests --with-marvin --marvin-config=/Users/wrodrigues/sbp_dev/cloudstack_integration_tests/cit/integration/acs/config/devcloud-advanced.cfg -s -a tags=advanced,required_hardware=false test_redundant_vpc.py

== Remarks

Add your Marvin source to the PYTHONPATH environment variable!

Ex.:

$ cd ~/cloudstack/tools/marvin
$ export PYTHONPATH=.

Now test it with:

$ python
$ >>> import marvin

There should be no error!

Have fun! :)
