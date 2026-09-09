# License LGPL-3.0-or-later. See LICENSE and NOTICE.
from odoo import _
from odoo.exceptions import UserError


def pre_init_hook(env):
    """Do not install two addons that own the same extension field.

    This hook does not migrate, uninstall, rename or delete any business data.
    A rename of an installed addon requires a separate, tested migration.
    """
    legacy = env["ir.module.module"].sudo().search_count([
        ("name", "=", "ranvals_crm_stage_company"),
        ("state", "in", ["installed", "to install", "to upgrade", "to remove"]),
    ], limit=1)
    if legacy:
        raise UserError(_(
            "The previous Company Stages addon is already installed or scheduled "
            "for a module operation. Do not install both addons together or "
            "uninstall the previous addon to rename it. Back up the database "
            "and complete a tested technical-name migration first."
        ))
