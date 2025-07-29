Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.

`4.0.0`_ - 2025-05-28
---------------------

This version requires AlekSIS-Core 4.0. It is incompatible with any previous
version.

`3.0`_ - 2023-05-15
-------------------

Nothing changed.

`3.0b0`_ - 2023-02-22
---------------------

This version requires AlekSIS-Core 3.0. It is incompatible with any previous
version.

`2.2`_ - 2022-06-23
-------------------

Added
~~~~~

* Add Ukrainian locale (contributed by Sergiy Gorichenko from Fre(i)e Software GmbH).

Fixed
~~~~~

* Remove preferences for the not yet available functionality to create LDAP users on register.

`2.1`_ - 2022-01-21
-------------------

Added
~~~~~

* Person field matching can now be matched disjunctive

Changed
~~~~~~~

* Update German translations.

Fixed
~~~~~

* A preference was not properly registered in the preference registry

`2.0.1`_ - 2021-11-29
---------------------

Fixed
~~~~~

* Account is not connected to a person on first login
* Migration of preference names failed in some cases

`2.0`_ - 2021-10-30
-------------------

Fixed
~~~~~

* Do not errornously handle password change/reset for non-LDAP users.

`2.0rc2`_ - 2021-09-16
----------------------

Fixed
~~~~~

* Names of preferences contained `__` in some rare cases which is forbidden.

`2.0rc1`_ - 2021-06-23
----------------------

Changed
~~~~~~~

* Add verbose name for preference section.

Fixed
~~~~~

* Preferences were evaluated before the app was ready.
* Disable LDAP sync by default to prevent loading with unexpected settings.
* Gracefully fail on missing LDAP data attributes.

`2.0b0`_ - 2021-05-21
---------------------

Changed
~~~~~~~

* Add automatic linking of groups to current school term while importing.

Removed
~~~~~~~

* Remove POSIX-specific code.

`2.0a2`_ - 2020-05-04
---------------------

Added
~~~~~

* Configurable sync strategies
* Management commands for ldap import
* Mass import of users and groups
* Sync LDAP users and groups on login

----------


.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html


.. _2.0a2: https://edugit.org/AlekSIS/official/AlekSIS-App-LDAP/-/tags/2.0a2
.. _2.0b0: https://edugit.org/AlekSIS/official/AlekSIS-App-LDAP/-/tags/2.0b0
.. _2.0rc1: https://edugit.org/AlekSIS/official/AlekSIS-App-LDAP/-/tags/2.0rc1
.. _2.0rc2: https://edugit.org/AlekSIS/official/AlekSIS-App-LDAP/-/tags/2.0rc2
.. _2.0: https://edugit.org/AlekSIS/official/AlekSIS-App-LDAP/-/tags/2.0
.. _2.0.1: https://edugit.org/AlekSIS/official/AlekSIS-App-LDAP/-/tags/2.0.1
.. _2.1: https://edugit.org/AlekSIS/official/AlekSIS-App-LDAP/-/tags/2.1
.. _2.2: https://edugit.org/AlekSIS/official/AlekSIS-App-LDAP/-/tags/2.2
.. _3.0b0: https://edugit.org/AlekSIS/official/AlekSIS-App-LDAP/-/tags/3.0b0
.. _3.0: https://edugit.org/AlekSIS/official/AlekSIS-App-LDAP/-/tags/3.0
.. _4.0.0: https://edugit.org/AlekSIS/official/AlekSIS-App-LDAP/-/tags/3.0
