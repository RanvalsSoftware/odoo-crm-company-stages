# Source review — 2026-09-09

Starting point: the user-supplied Odoo 19 company-stage addon (LGPL-3.0-or-later).
No private GitHub repository code was incorporated into the new release.

Primary upstream excerpts inspected using the connected GitHub tool:

| Source | Ref | Blob SHA | Relevant difference |
|---|---|---|---|
| odoo/odoo addons/crm/models/crm_lead.py | 17.0 | a2a000fae9f1cb742d428a2de5eadc58ece0a1d5 | group expansion takes order; stage.team_id |
| odoo/odoo addons/crm/models/crm_lead.py | 18.0 | 6f718cf9d38f829fb4999123b33f82459740100c | no order parameter; stage.team_id |
| odoo/odoo addons/crm/models/crm_stage.py | 18.0 | 678ae3e268eb0c31cc24fab9736fffd0a63198d8 | native optional team_id, default_get |
| odoo/odoo addons/crm/views/crm_stage_views.xml | 17.0 | c3799b120cd67edd72b948d256b8431dccd20962 | tree; team_id |
| odoo/odoo addons/crm/views/crm_stage_views.xml | 18.0 | 06fee9845f9ecb59c13fd098d45b9d554970f2d0 | list; team_id |
| odoo/odoo addons/crm/views/crm_stage_views.xml | 19.0 | 2f38c55df83e4fd9f6d2b41e6f26c77b2f348958 | list; team_ids |
| odoo/odoo odoo/modules/loading.py | 17.0 | c0a57e010f1c646d58f1d14050d2351f5c382856 | pre_init_hook receives env |

Source URLs follow https://github.com/odoo/odoo/blob/REF/PATH for each table entry.
The local XPath checks use small structural fixtures, not a complete upstream or
live inherited view. Reviewing source is not a substitute for executing Odoo tests.
