clusterctl.py
=============

Slightly improved control script for 8086.net's clusterhat.

While their clusterhat script provides power control of attached pi zeros, it does not provide for clean shutdown of them before removing power. This script attempt to provide this.

Assumptions & Requirements
-----------
1. Controller pi and pi zeros have been setup using the images from clusterhat.com
2. The python-pip and python-gpiozero packages have been installed on the controller pi.
3. Pi zeros have been configured to allow ssh and passwordless login via keys from the controlling pi.

Installation
------------
1. Download gpiosetup.sh and clusterctl.py
2. Configure raspbian such that root runs gpiosetup.sh at each boot.

More detailed instructions can be found in install.md

Configuration
-------------
Configuration should not be neccessary if using the images mentioned above. If not, edit clusterctl.py and change values in the constants section (lines 12 through 42) as needed.


Usage
-----
```
usage: clusterctl.py [-h] [--hard] [-v] [-n NODES] [-c COMMAND]
                     [{stop,start,restart,status}]

Perform action on nodes attached to a clusterhet.

positional arguments:
  {stop,start,restart,status}
                        action to be performed.

optional arguments:
  -h, --help            show this help message and exit
  --hard                don't attempt clean shutdown or restart. Just switch
                        node power instead. Report only power state, don't
                        attempt to check whether server is responsive.
  -v, --verbose
  -n NODES, --nodes NODES
                        List of nodes to target e.g. 123. Action is applied to
                        all nodes when not present.
  -c COMMAND            run "COMMAND" on node(s). "COMMAND" is passed to the
                        node(s) as is. No validation is performed.
```
clusterctl.py does not need to be run as root.