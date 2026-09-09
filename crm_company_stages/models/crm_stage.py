# Copyright 2026 CRM Company Stages contributors
# See NOTICE for original attribution.
# License LGPL-3.0-or-later.
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmStage(models.Model):
    _inherit = "crm.stage"

    # Deliberately NO field default: Odoo would otherwise backfill existing
    # stages with the installer's current company when adding this column.
    # default_get supplies the default only for NEW records instead.
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        ondelete="restrict",
        help=(
            "This stage belongs to the selected company. Leave empty to share "
            "it across companies. Sales team restrictions still apply."
        ),
    )

    @api.model
    def _company_stages_default_company_id(self):
        """Respect an explicit shared default, then the pipeline's team."""
        context = self.env.context
        if "default_company_id" in context:
            return context["default_company_id"] or False
        team_id = context.get("default_team_id")
        if team_id:
            team = self.env["crm.team"].browse(team_id).exists()
            if team.company_id:
                return team.company_id.id
        return self.env.company.id

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        if "company_id" in fields_list and "company_id" not in values:
            # Template data loaded by another module stays shareable, just like
            # the stages which existed before this addon was installed.
            values["company_id"] = (
                False
                if self.env.context.get("install_mode")
                else self._company_stages_default_company_id()
            )
        return values

    @api.constrains("company_id", "team_id")
    def _check_stage_company_links(self):
        """Check reverse links too; a lead constraint alone cannot do this.

        sudo is confined to integrity checks so archived and otherwise hidden
        records cannot be orphaned. No foreign record names are disclosed.
        """
        Lead = self.env["crm.lead"].sudo().with_context(active_test=False)
        for stage in self.sudo():
            company = stage.company_id
            if not company:
                continue
            if any(team.company_id and team.company_id != company for team in stage.team_id):
                raise ValidationError(_(
                    "A company-specific stage cannot be linked to a sales team "
                    "of another company. Choose a matching or shared sales team."
                ))
            incompatible_leads = Lead.search_count([
                ("stage_id", "=", stage.id),
                "|",
                ("company_id", "=", False),
                ("company_id", "!=", company.id),
            ], limit=1)
            if incompatible_leads:
                raise ValidationError(_(
                    "This stage is used by leads or opportunities belonging to "
                    "another company, or with no company, including archived "
                    "records. Move those records to a suitable stage first, "
                    "or keep this stage shared. No opportunities were moved."
                ))
