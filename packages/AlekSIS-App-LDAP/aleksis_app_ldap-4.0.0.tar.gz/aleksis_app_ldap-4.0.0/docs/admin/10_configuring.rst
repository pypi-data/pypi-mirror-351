Configuring LDAP synchronisation
================================

Setting up the LDAP synchronisation consists of three parts, which
together make up the process of updating persons and groups from
LDAP information.

All preferences are set under *Admin → Configuration → LDAP*.

The synchronisation always starts from a user account. Therefore,
LDAP authentication needs to set up first.

Matching fields
~~~~~~~~~~~~~~~

The first step is to configure *matching fields*. This configuration
defines how persons are found in AlekSIS, based on fields in LDAP.
The relevant settings are:

* **LDAP sync matching mode**: Setting this preference to *OR* means
  that at least one of the fields must match, whereas *AND* means all
  fields must match
* **LDAP sync fields**: This list defines which fields of the person
  in AlekSIS are considered for matching persons to LDAP entries

Field matching and rewriting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For all fields (both matching fields and other imported fields), the
behaviour of the fields needs to be considered.

For every available field of a Person, the following preferences are
available:

* **LDAP field for…**: This defines which LDAP attribute the data
  for this field is pulled from
* **Regular expression to match LDAP value for…**: If set, defines
  a regular expression that is applied to the attribute data from LDAP.
  The regular expression can contain named groups (see the `Python
  Documentation on Named Groups`_)
* **Replacement template to apply to…**: This template is applied to
  the LDAP data, and it can reference the groups matched in the
  regular expression defined for this field using ``\g<name>``

Only fields that are configured here are honoured by the import,
all other fields are ignored.

For synchronising groups, the same preferences are provided for the
names and short names of the group.

Setting up what and when to synchronise
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, the LDAP import can be enabled by setting up the last preferences,
which define when the LDAP import is run.

* **Create missing persons for LDAP users**: Defines whether persons
  which are not found by the matching fields are created
* **Sync LDAP user with person on login**: If this preference is enabled,
  persons are updated from LDAP on every login
* **Enable LDAP group sync**: If enabled, all groups the synchronised
  users are members of are also imported

.. warning::
   You should take special care to thoroughly test your LDAP configuration.
   If operating on production data with a faulty sync configuration, important
   data might be overriden and destroyed.

.. _Python Documentation on Named Groups: https://docs.python.org/3/howto/regex.html#non-capturing-and-named-groups
