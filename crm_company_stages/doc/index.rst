CRM Company Stages
==================

Free, open-source company-specific pipeline stages for Odoo 17.0.
The addon extends the existing CRM interface; it does not add a separate app menu.

Features
--------
* Set a Company in a stage's gear > Edit dialog.
* Leave Company empty to share the stage (sales-team restrictions still apply).
* Filter both populated and empty pipeline columns by selected companies.
* Keep opportunity stages consistent with their company during create/write/import.
* Prevent incompatible stage/team company changes, including archived opportunities.
* Handle bulk Won actions separately by company and sales team.

Important behavior
------------------
The company selector controls visibility. With A and B both selected, both
companies' stages are visible. Select only A to hide B's stages. This is not
an extra CRM tag system or a replacement for opportunity access rights.
Existing stages remain shared on a fresh installation. No opportunities are
moved, deleted or assigned to a company automatically.

Installation
------------
Install on Odoo.sh or a self-hosted matching Odoo version with the CRM addon.
Copy the ``crm_company_stages`` directory into an addons path, restart Odoo,
update the Apps list, remove the default Apps filter if needed, and install
CRM Company Stages. This Python addon is not installable on standard Odoo Online.
Back up first and test using a disposable database before production use.

Legacy addon
------------
Do not install alongside the previous ``ranvals_crm_stage_company`` addon.
The pre-install hook blocks this combination. Do not uninstall the old addon
just to change its technical name: a dedicated migration is required.

Testing
-------
38 Odoo integration test methods are included. They have NOT been executed in
an Odoo/PostgreSQL runtime in this preparation environment. See QA_REPORT_TR.md.
Run: ``odoo -d disposable_test -i crm_company_stages --test-enable
--test-tags /crm_company_stages --stop-after-init --without-demo=all``.

License and privacy
-------------------
LGPL-3.0-or-later; see LICENSE, COPYING and NOTICE. No license server,
subscription, API key, telemetry, external service or paid dependency is added.
The Odoo software/licensing/hosting costs are separate from this free addon.
Community support has no promised response time. Report issues through the
publishing repository after it has been created.

See ``doc/index.rst`` and ``README_TR.md`` for usage and deployment notes.
