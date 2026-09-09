# CRM Company Stages

Free, open-source company-specific CRM stages for Odoo 17, 18 and 19.
Technical name: `crm_company_stages`. License: LGPL-3.0-or-later.

## Addon branches

| Odoo | Branch | Addon directory |
|---|---|---|
| 17 | [17.0](https://github.com/RanvalsSoftware/odoo-crm-company-stages/tree/17.0) | `crm_company_stages/` |
| 18 | [18.0](https://github.com/RanvalsSoftware/odoo-crm-company-stages/tree/18.0) | `crm_company_stages/` |
| 19 | [19.0](https://github.com/RanvalsSoftware/odoo-crm-company-stages/tree/19.0) | `crm_company_stages/` |

`main` contains the standalone promotional site under `docs/` and publication documentation.
The module has no price or paid dependency. Other repositories are unaffected.

## What it does

Scope CRM pipeline stages (including empty columns) to a company, while keeping
shared stages and native sales-team restrictions. The same salesperson can work
across companies. Select one company for a separated pipeline; selecting both
intentionally shows both companies' stages. This addon scopes stages, not tags.

## Validation

The publication workflow runs the provided 38 Odoo integration tests for **each**
version in disposable Odoo/PostgreSQL containers before creating version branches.
Review the [workflow runs](https://github.com/RanvalsSoftware/odoo-crm-company-stages/actions) for actual results and commit references.
Static validation covers 552 domain cases across the three versions. Browser
smoke tests on the target installation remain recommended.

The demonstration graphics are illustrations, not real Odoo screenshots.
The build regenerates the original supplied HTML artwork as PNG files.

## Installation and migration

Use the branch matching your Odoo version and add `crm_company_stages` to your
addons path. Update Apps and install CRM Company Stages (remove the Apps filter
when necessary). Do not install beside `ranvals_crm_stage_company`. Renaming an
installed addon requires a backed-up, separately tested technical-name migration;
do not uninstall the original addon merely to change its name.

## Website and Odoo Apps

The site and version ZIPs are in `docs/`. To host using GitHub Pages, choose
**Settings > Pages > Deploy from a branch > main > /docs**. The intended site is
https://ranvalssoftware.github.io/odoo-crm-company-stages/ .

A GitHub release is not an Odoo Apps listing. The publisher must register this
repository and its version branches in the Odoo Apps vendor portal. Read
`PUBLISH_TR.md` for submission details.

Independent third-party addon. Not an official Odoo product or endorsement.
Original attribution is retained in `NOTICE`. See `LICENSE` and `COPYING`.
