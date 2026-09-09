# Copyright 2026 CRM Company Stages contributors
# See NOTICE for original attribution.
# License LGPL-3.0-or-later.
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Domain


class CrmLead(models.Model):
    _inherit = "crm.lead"

    # Preserve the native compute/tracking/group_expand/ondelete settings.
    # Native crm.lead already enables _check_company_auto. This check protects
    # create/write/import/RPC and drag-and-drop, not only the form dropdown.
    stage_id = fields.Many2one(
        check_company=True,
        domain=(
            "['&', '|', ('company_id', '=', False), "
            "('company_id', '=', company_id), '|', "
            "('team_ids', '=', False), ('team_ids', 'in', team_id)]"
        ),
    )

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        # Native CRM expands empty stage columns with elevated access. Keep its team and
        # existing-column logic, then explicitly reapply company scope AND
        # the caller's ordinary record rules. Never return the sudo search.
        expanded = super()._read_group_stage_ids(stages, domain)
        stage_domain = Domain("id", "in", expanded.ids) & Domain(
            "company_id", "in", self.env.companies.ids + [False]
        )
        return self.env["crm.stage"].search(stage_domain, order=stages._order)

    def _stage_find(self, team_id=False, domain=None, order="sequence, id", limit=1):
        """Choose stages using the lead company, not the salesperson's company.

        A genuinely company-less lead can only use shared stages. For a mixed
        recordset only a shared stage is safe; action_set_won splits its batch
        before it reaches this method.
        """
        if self:
            company_ids = {lead.company_id.id or False for lead in self}
            company_id = next(iter(company_ids)) if len(company_ids) == 1 else False
        elif "default_company_id" in self.env.context:
            company_id = self.env.context["default_company_id"] or False
        elif team_id:
            team = self.env["crm.team"].browse(team_id).exists()
            company_id = team.company_id.id or self.env.company.id
        else:
            company_id = self.env["crm.stage"]._company_stages_default_company_id()

        permitted = [False, company_id] if company_id else [False]
        stage_domain = Domain(domain or []) & Domain("company_id", "in", permitted)
        return super()._stage_find(
            team_id=team_id, domain=stage_domain, order=order, limit=limit
        )

    def action_set_won(self):
        # Native CRM uses the whole recordset in _stage_find even inside
        # its per-lead loop. Split by company AND team to avoid choosing another
        # company's/team's won stage for a multi-selection action.
        groups = {}
        for lead in self:
            key = (lead.company_id.id, lead.team_id.id)
            groups[key] = groups.get(key, self.browse()) | lead
        for leads in groups.values():
            if not leads._stage_find(domain=[("is_won", "=", True)]):
                raise UserError(_(
                    "No suitable Won stage is available for one of the selected "
                    "companies or sales teams. Configure a matching or shared "
                    "Won stage before marking these opportunities as won."
                ))
        for leads in groups.values():
            super(CrmLead, leads).action_set_won()
        return True
