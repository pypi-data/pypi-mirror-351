Interfacing with an LDAP directory beyond authentication
========================================================

In addition to authenticating agains an LDAP directory (as laid out
in :ref:`core-ldap`), AlekSIS can import personal information from
LDAP. This functionality is currently limited to the information about
persons and groups (cf. :ref:`core-concept-person` and :ref:`core-concept-group`),
and related inforamtion.

Data can only be synchronised one-way. That means that, if you wish to
continue maintaining personal information in LDAP, you should ensure
that all changes are made in LDAP first, and then imported to AlekSIS.
