# Odoo 20 runtime validation

CRM Company Stages `20.0.1.0.0` was installed from this branch into a clean,
disposable Odoo 20 Community database backed by PostgreSQL 17 on 7 October 2026.

- Module installation: PASS
- 38 addon integration test methods discovered and executed: PASS
- Odoo-reported result: 40 tests, 0 failures, 0 errors
- Static validation: PASS (208 company/team/domain combinations)
- Inherited CRM view selectors loaded against the real Odoo 20 views: PASS

The Odoo 20 port replaces the legacy `ir.rule` XML record with Odoo 20's
unified global `ir.access.csv` restriction while preserving all four CRUD
operations and the selected-company/shared-stage domain.

This is a Community runtime check, not a guarantee for every Enterprise,
Studio, browser or third-party customization combination. Back up production
databases and perform deployment-specific staging checks before upgrading.
