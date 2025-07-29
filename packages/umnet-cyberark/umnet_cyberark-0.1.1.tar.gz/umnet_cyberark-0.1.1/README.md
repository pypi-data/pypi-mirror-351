# umnet-cyberark
Python library for doing API calls to cyberark.

Note that this code was adapted from a class in `umnet-scripts` so that it can be imported separately from that library.
Originally authored by Jeff Hagley, I've added some error checking and convenience methods. Reference:
https://github.com/umich-its-networking/umnet-scripts/blob/master/umnet_scripts/cyberark.py

As of May 2025 this code is only intended to be used by other libraries. Install with pip:
```
pip install umnet-cyberark
```
Then in your code you can import and use it like so:
```
from umnet_cyberark import Cyberark

c = Cyberark(env_file="/usr/local/umnet/lib/cyberark/cyberark.env")
c.lookup_username_password("automaton")
```
You need a `cyberark.env` file that has paths to the keys and certs for the `UMNET` and/or `NSO` environments.
If you don't provide this as an argument it will assume it's in your current directory (eg `cyberark.env`)
