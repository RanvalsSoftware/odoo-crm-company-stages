# Copyright 2026 CRM Company Stages contributors
# See NOTICE for original attribution.
# License LGPL-3.0-or-later.
"""Odoo 17 integration tests. Run only in a disposable/staging database.

These tests require a running Odoo test environment and PostgreSQL. They are
not substitutes for the separately reported static package validation.
"""
from lxml import etree

from odoo import Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged("post_install", "-at_install")
class TestStageCompany(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a, cls.company_b, cls.company_c = cls.env["res.company"].sudo().create([
            {"name": "Stage QA A"},
            {"name": "Stage QA B"},
            {"name": "Stage QA C"},
        ])
        companies = [cls.company_a.id, cls.company_b.id]
        cls.manager = new_test_user(
            cls.env, login="stage_company_manager",
            groups="sales_team.group_sale_manager,base.group_multi_company",
            company_id=cls.company_a.id,
            company_ids=[Command.set(companies)],
        )
        cls.salesperson = new_test_user(
            cls.env, login="stage_company_salesperson",
            groups="sales_team.group_sale_salesman,base.group_multi_company",
            company_id=cls.company_a.id,
            company_ids=[Command.set(companies)],
        )
        cls.ctx = {
            "allowed_company_ids": companies,
            "install_mode": False,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "tracking_disable": True,
        }
        cls.Stage = cls.env["crm.stage"].with_user(cls.manager).with_context(**cls.ctx)
        cls.Lead = cls.env["crm.lead"].with_user(cls.manager).with_context(**cls.ctx)
        cls.Team = cls.env["crm.team"].with_user(cls.manager).with_context(**cls.ctx)
        cls.shared_team = cls.Team.create({
            "name": "QA shared team", "company_id": False,
            "member_ids": [Command.set([cls.salesperson.id])],
        })
        cls.team_a, cls.team_b = cls.Team.create([
            {"name": "QA team A", "company_id": cls.company_a.id},
            {"name": "QA team B", "company_id": cls.company_b.id},
        ])
        cls.stage_a, cls.stage_b, cls.shared_stage, cls.won_a, cls.won_b = cls.Stage.create([
            {"name": "QA A", "company_id": cls.company_a.id, "sequence": -100},
            {"name": "QA B", "company_id": cls.company_b.id, "sequence": -101},
            {"name": "QA shared", "company_id": False, "sequence": 900},
            {"name": "QA won A", "company_id": cls.company_a.id, "is_won": True, "sequence": -50},
            {"name": "QA won B", "company_id": cls.company_b.id, "is_won": True, "sequence": -50},
        ])

    def _lead(self, company=None, stage=None, **extra):
        company = self.company_a if company is None else company
        values = {
            "name": "QA opportunity",
            "type": "opportunity",
            "company_id": company.id if company else False,
            "team_id": self.shared_team.id if company else False,
            "user_id": self.salesperson.id if company else False,
        }
        if stage is not None:
            values["stage_id"] = stage.id if stage else False
        values.update(extra)
        return self.Lead.create(values)

    def test_01_new_stage_defaults_to_current_company(self):
        self.assertEqual(self.Stage.create({"name": "Default A"}).company_id, self.company_a)

    def test_02_company_switch_changes_default(self):
        stage = self.Stage.with_company(self.company_b).create({"name": "Default B"})
        self.assertEqual(stage.company_id, self.company_b)

    def test_03_explicit_shared_stage_is_preserved(self):
        stage = self.Stage.create({"name": "Explicit shared", "company_id": False})
        self.assertFalse(stage.company_id)

    def test_04_context_shared_default_is_preserved(self):
        stage = self.Stage.with_context(default_company_id=False).create({"name": "Shared context"})
        self.assertFalse(stage.company_id)

    def test_05_context_company_default_is_preserved(self):
        stage = self.Stage.with_context(default_company_id=self.company_b.id).create({"name": "B context"})
        self.assertEqual(stage.company_id, self.company_b)

    def test_06_team_context_controls_new_stage_company(self):
        stage = self.Stage.with_context(default_team_id=self.team_b.id).create({"name": "B team context"})
        self.assertEqual(stage.company_id, self.company_b)

    def test_07_field_has_no_install_time_backfill_default(self):
        self.assertIsNone(self.Stage._fields["company_id"].default)
        self.assertFalse(self.Stage.with_context(install_mode=True).default_get(["company_id"])["company_id"])
        self.assertNotIn("company_id", self.Stage.default_get(["name"]))

    def test_08_record_rule_single_company_a(self):
        stages = self.Stage.with_context(allowed_company_ids=[self.company_a.id]).search([])
        self.assertIn(self.stage_a, stages)
        self.assertIn(self.shared_stage, stages)
        self.assertNotIn(self.stage_b, stages)

    def test_09_record_rule_single_company_b(self):
        stages = self.Stage.with_context(allowed_company_ids=[self.company_b.id]).search([])
        self.assertIn(self.stage_b, stages)
        self.assertIn(self.shared_stage, stages)
        self.assertNotIn(self.stage_a, stages)

    def test_10_both_selected_companies_remain_visible(self):
        stages = self.Stage.search([])
        self.assertIn(self.stage_a, stages)
        self.assertIn(self.stage_b, stages)

    def test_11_direct_read_of_unselected_company_denied(self):
        stage = self.stage_b.with_context(allowed_company_ids=[self.company_a.id])
        with self.assertRaises(AccessError):
            stage.read(["name"])

    def test_12_create_for_unauthorized_company_denied(self):
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.Stage.create({"name": "Unauthorized", "company_id": self.company_c.id})

    def test_13_salesperson_stage_management_acl_is_unchanged(self):
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.Stage.with_user(self.salesperson).create({"name": "Not a manager"})
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.stage_a.with_user(self.salesperson).write({"name": "Not allowed"})

    def test_14_cross_company_stage_create_is_blocked(self):
        with self.assertRaises(UserError), self.cr.savepoint():
            self._lead(self.company_a, self.stage_b)

    def test_15_cross_company_drag_or_rpc_write_is_blocked(self):
        lead = self._lead(self.company_a, self.stage_a)
        with self.assertRaises(UserError), self.cr.savepoint():
            lead.write({"stage_id": self.stage_b.id})
        self.assertEqual(lead.stage_id, self.stage_a)

    def test_16_companyless_lead_cannot_use_private_stage(self):
        with self.assertRaises(UserError), self.cr.savepoint():
            self._lead(False, self.stage_a)

    def test_17_shared_stage_works_in_both_companies(self):
        a = self._lead(self.company_a, self.shared_stage)
        b = self._lead(self.company_b, self.shared_stage)
        self.assertEqual(a.stage_id, b.stage_id)
        self.assertEqual(a.user_id, b.user_id)

    def test_18_new_lead_stage_selection_uses_its_company(self):
        a = self._lead(self.company_a)
        b = self._lead(self.company_b)
        self.assertEqual(a.stage_id, self.stage_a)
        self.assertEqual(b.stage_id, self.stage_b)

    def test_19_stage_find_uses_record_not_current_company(self):
        lead_b = self._lead(self.company_b, self.stage_b)
        self.assertEqual(lead_b.env.company, self.company_a)
        found = lead_b._stage_find()
        self.assertEqual(found, self.stage_b)

    def test_20_companyless_stage_find_is_shared_only(self):
        lead = self._lead(False, self.shared_stage)
        found = lead._stage_find(limit=None)
        self.assertTrue(found)
        self.assertFalse(any(found.mapped("company_id")))

    def test_21_empty_model_stage_find_respects_context(self):
        self.assertEqual(self.Lead.with_context(default_company_id=self.company_b.id)._stage_find(), self.stage_b)
        found = self.Lead.with_context(default_company_id=False)._stage_find(limit=None)
        self.assertFalse(any(found.mapped("company_id")))

    def test_22_empty_kanban_columns_are_company_filtered(self):
        lead_model = self.Lead.with_context(allowed_company_ids=[self.company_a.id])
        columns = lead_model._read_group_stage_ids(lead_model.env["crm.stage"], [], "sequence, name, id")
        self.assertIn(self.stage_a, columns)
        self.assertIn(self.shared_stage, columns)
        self.assertNotIn(self.stage_b, columns)
        self.assertNotIn(self.won_b, columns)

    def test_23_group_expansion_cannot_reintroduce_foreign_stage(self):
        lead_model = self.Lead.with_context(allowed_company_ids=[self.company_a.id])
        supplied = lead_model.env["crm.stage"].browse([self.stage_a.id, self.stage_b.id])
        columns = lead_model._read_group_stage_ids(supplied, [], "sequence, name, id")
        self.assertIn(self.stage_a, columns)
        self.assertNotIn(self.stage_b, columns)

    def test_24_group_expansion_keeps_native_team_restrictions(self):
        other_team = self.Team.create({"name": "Other A team", "company_id": self.company_a.id})
        restricted = self.Stage.create({
            "name": "Restricted A", "company_id": self.company_a.id,
            "team_id": other_team.id,
        })
        lead_model = self.Lead.with_context(
            allowed_company_ids=[self.company_a.id],
            default_team_id=self.team_a.id, show_user_team_stages=False,
        )
        columns = lead_model._read_group_stage_ids(lead_model.env["crm.stage"], [], "sequence, name, id")
        self.assertNotIn(restricted, columns)
        # A populated column is retained by the native expansion logic.
        columns = lead_model._read_group_stage_ids(restricted, [], "sequence, name, id")
        self.assertIn(restricted, columns)

    def test_25_stage_reassignment_checks_other_company_leads(self):
        self._lead(self.company_b, self.shared_stage)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.shared_stage.write({"company_id": self.company_a.id})
        self.assertFalse(self.shared_stage.company_id)

    def test_26_stage_reassignment_also_checks_archived_leads(self):
        self._lead(self.company_b, self.shared_stage, active=False)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.shared_stage.write({"company_id": self.company_a.id})

    def test_27_stage_reassignment_also_checks_companyless_leads(self):
        self._lead(False, self.shared_stage)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.shared_stage.write({"company_id": self.company_a.id})

    def test_28_compatible_existing_stage_can_be_assigned(self):
        lead = self._lead(self.company_a, self.shared_stage)
        self.shared_stage.write({"company_id": self.company_a.id})
        self.assertEqual(lead.stage_id, self.shared_stage)
        self.assertEqual(lead.company_id, self.company_a)

    def test_29_private_stage_rejects_foreign_team(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.stage_a.write({"team_id": self.team_b.id})

    def test_30_shared_stage_can_restrict_a_company_team(self):
        self.shared_stage.write({"team_id": self.team_b.id})
        self.assertEqual(self.shared_stage.team_id, self.team_b)
        self.assertFalse(self.shared_stage.company_id)

    def test_31_team_company_change_cannot_invalidate_stage(self):
        self.stage_a.write({"team_id": self.team_a.id})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.team_a.write({"company_id": self.company_b.id})

    def test_32_bulk_won_action_uses_each_company_won_stage(self):
        a = self._lead(self.company_a, self.stage_a)
        b = self._lead(self.company_b, self.stage_b)
        (a | b).action_set_won()
        self.assertEqual(a.stage_id, self.won_a)
        self.assertEqual(b.stage_id, self.won_b)
        self.assertEqual(a.probability, 100)
        self.assertEqual(b.probability, 100)

    def test_33_missing_won_stage_gives_clear_error(self):
        self.Stage.search([
            ("is_won", "=", True),
            ("company_id", "in", [False, self.company_a.id]),
        ]).write({"is_won": False})
        lead = self._lead(self.company_a, self.stage_a)
        with self.assertRaises(UserError), self.cr.savepoint():
            lead.action_set_won()
        self.assertEqual(lead.stage_id, self.stage_a)

    def test_34_company_and_stage_can_be_changed_together(self):
        lead = self._lead(self.company_a, self.stage_a)
        lead.write({"company_id": self.company_b.id, "stage_id": self.stage_b.id})
        self.assertEqual(lead.company_id, self.company_b)
        self.assertEqual(lead.stage_id, self.stage_b)

    def test_35_stage_edit_modal_has_company_field(self):
        view_id = self.env.ref("crm.crm_stage_form").id
        arch = self.Stage.get_view(view_id=view_id, view_type="form")["arch"]
        root = etree.fromstring(arch.encode())
        fields = root.xpath("//field[@name='company_id']")
        self.assertEqual(len(fields), 1)
        self.assertEqual(fields[0].getnext().get("name"), "team_id")

    def test_36_opportunity_statusbar_has_company_domain(self):
        view_id = self.env.ref("crm.crm_lead_view_form").id
        arch = self.Lead.get_view(view_id=view_id, view_type="form")["arch"]
        root = etree.fromstring(arch.encode())
        field = root.xpath("//header/field[@name='stage_id']")[0]
        self.assertIn("company_id", field.get("domain"))

    def test_37_company_change_alone_cannot_keep_foreign_stage(self):
        lead = self._lead(self.company_a, self.stage_a)
        with self.assertRaises(UserError), self.cr.savepoint():
            lead.write({"company_id": self.company_b.id})
        self.assertEqual(lead.company_id, self.company_a)

    def test_38_expanded_columns_do_not_elevate_access(self):
        lead_model = self.Lead.with_context(allowed_company_ids=[self.company_a.id])
        columns = lead_model._read_group_stage_ids(lead_model.env["crm.stage"], [], "sequence, name, id")
        self.assertFalse(columns.env.su)
        self.assertEqual(columns.env.uid, self.manager.id)
