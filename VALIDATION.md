# Runtime validation

Integration jobs passed before publication: [workflow run](https://github.com/RanvalsSoftware/odoo-crm-company-stages/actions/runs/34346220917).

Source preparation commit: `21cda93ffa7116afd5997a934f2b26ada880725a`.

Odoo 17.0, 18.0 and 19.0 were each installed with CRM Company Stages in disposable Odoo/PostgreSQL containers. The provided 38 addon tests were discovered and checked for each version. All matrix jobs are required to succeed before this report and the branches can be published.

Static validation: 552 company/team/domain combinations across the three versions.

These are Community runtime checks, not a guarantee for every Enterprise combination or customer customization. Browser smoke tests and backups remain necessary. No production/customer database was used.
