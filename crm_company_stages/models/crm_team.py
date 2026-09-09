# Copyright 2026 CRM Company Stages contributors
# See NOTICE for original attribution.
# License LGPL-3.0-or-later.
from odoo import _, api, models
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = "crm.team"

    @api.constrains("company_id")
    def _check_stage_company(self):
        # A later company change on a team must not silently invalidate a
        # previously valid company-specific stage linked to that team.
        Stage = self.env["crm.stage"].sudo()
        for team in self.sudo():
            if team.company_id and Stage.search_count([
                ("team_ids", "in", team.ids),
                ("company_id", "!=", False),
                ("company_id", "!=", team.company_id.id),
            ], limit=1):
                raise ValidationError(_(
                    "This sales team is linked to a stage of another company. "
                    "Update the stage's sales teams before changing the team's company."
                ))
