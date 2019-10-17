# LDAP

django-auth-ldap need python_ldap package

On windows python_ldap package can be installed in wheel form (compiled):

Download needed python_ldap wheels depending on your platform / python version
https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-ldap

Then install it (example for cPython 3.7 on 64 bit Windows)
pip install wheels/python_ldap-3.2.0-cp37-cp37m-win_amd64.whl