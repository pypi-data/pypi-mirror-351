Managing user accounts in LDAP
==============================

While not allowing to synchronise full personal information back
into LDAP, AlekSIS has limited support for managing user accounts
(i.e. limited to pure authentication information) in LDAP.

Changing passwords in LDAP
--------------------------

When users change their password in AlekSIS, it can also be changed
in LDAP. This requires one of two prerequisites:

* Users must be allowed to change their own passwords in LDAP,
  by setting appropriate ACLs
* In the AlekSIS preferences, the credentials of an account
  with sufficient ACLs to change all users' passwords must be
  configured in the respective preferences

.. warning::

   Providing admin credentials to AlekSIS imposes obvious security
   risks. Thus, make sure to limit this account to changing passwords.
   Also, make sure that other, security-critical systems which authenticate
   against LDAP, and AlekSIS itself, require a second factor for administration,
   so attackers who manage to hijack an administrator account by changing its
   password cannot use it for anything else.

If you want to enable automatic password resets, an administrator account
has to be provided in all cases, because the user triggering the password
reset is not the user themselves. For more information on password resets,
see :ref:`core-password-resets`.

Creating LDAP users upon registration
-------------------------------------

If user invitations or registration are enabled, AlekSIS can create the respective
account in LDAP. In addition to providing admin credentials, the RDN fields
that shall make up the user DN need to be configured in preferences.

For details, see :ref:`core-registration`.
