#!/usr/bin/env python3
"""Static package checks only. Does NOT import, install or simulate Odoo.

The tiny XML fixtures below capture the relevant selector structure of the
reviewed upstream 19.0 views. They are not a copy of a live combined view.
Domain truth-table checks evaluate this module's literal domain expressions;
they do NOT execute Odoo ORM/security and must not be called integration tests.
"""
from __future__ import annotations

import ast
from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]

FIXTURES = {
    "crm.crm_stage_form": """<form><sheet><div class="oe_title"><field name="name"/></div>
        <group><group><field name="fold"/><field name="color"/><field name="team_ids"/></group>
        <group><field name="is_won"/><field name="rotting_threshold_days"/></group>
        <field name="team_count"/></group><separator/><field name="requirements"/></sheet></form>""",
    "crm.crm_stage_tree": """<list multi_edit="1"><field name="sequence"/><field name="name"/>
        <field name="is_won"/><field name="team_ids"/><field name="rotting_threshold_days"/></list>""",
    "crm.crm_lead_stage_search": """<search><field name="name"/><field name="sequence"/>
        <field name="is_won"/><field name="team_ids"/></search>""",
    "crm.crm_lead_view_form": """<form><header><field name="stage_id"/></header>
        <sheet><field name="company_id"/><field name="team_id"/></sheet></form>""",
    "crm.crm_case_kanban_view_leads": """<kanban><field name="stage_id"/>
        <field name="team_id"/><templates/></kanban>""",
}


def expression(source: str, **names):
    # Only evaluate literal expressions authored in this local package.
    return eval(compile(ast.parse(source, mode="eval"), "<package-domain>", "eval"),
                {"__builtins__": {}}, names)


def matches(domain: list, record: dict) -> bool:
    """Small truth-table evaluator for ONLY the operators used by this addon."""
    position = 0

    def leaf(term):
        field, op, wanted = term
        actual = record[field]
        if isinstance(actual, list):
            if op == "=" and wanted is False:
                return not actual
            if op == "in":
                values = wanted if isinstance(wanted, (list, tuple)) else [wanted]
                return bool(set(actual) & set(values))
        if op == "=":
            return actual == wanted
        if op == "!=":
            return actual != wanted
        if op == "in":
            return actual in wanted
        raise AssertionError(f"Unsupported operator in QA evaluator: {op}")

    def take():
        nonlocal position
        term = domain[position]
        position += 1
        if isinstance(term, str):
            if term == "!":
                return not take()
            left, right = take(), take()  # consume both, never short circuit
            if term == "&":
                return left and right
            if term == "|":
                return left or right
            raise AssertionError(f"Unexpected operator: {term}")
        return leaf(term)

    answers = []
    while position < len(domain):
        answers.append(take())
    return all(answers)


def field_call(tree: ast.AST, name: str):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            if isinstance(node.value, ast.Call):
                return node.value
    raise AssertionError(f"Field not found: {name}")


def main():
    manifest = ast.literal_eval((ROOT / "__manifest__.py").read_text(encoding="utf-8"))
    assert manifest["version"] == "19.0.1.0.0"
    assert manifest["depends"] == ["crm"]
    assert manifest["installable"] is True
    for name in manifest["data"]:
        assert (ROOT / name).is_file(), name

    assert manifest["name"] == "CRM Company Stages"
    assert not manifest.get("price", 0)
    assert manifest["license"] == "LGPL-3"
    assert manifest["pre_init_hook"] == "pre_init_hook"
    for image in manifest["images"]:
        assert (ROOT / image).is_file(), image
    assert (ROOT / "static/description/icon.png").is_file()
    from lxml import html
    page = html.fromstring((ROOT / "static/description/index.html").read_text())
    assert not page.xpath("//script|//iframe|//style|//link|//form")
    for element in page.iter():
        assert not any(k.lower().startswith("on") for k in element.attrib)
    for image in page.xpath("//img"):
        assert (ROOT / "static/description" / image.get("src")).is_file()
    py_files = list(ROOT.rglob("*.py"))
    trees = {}
    for path in py_files:
        trees[path.relative_to(ROOT).as_posix()] = ast.parse(path.read_text(encoding="utf-8"))
        compile(path.read_text(encoding="utf-8"), str(path), "exec")

    stage_call = field_call(trees["models/crm_stage.py"], "company_id")
    assert not any(kw.arg == "default" for kw in stage_call.keywords), "Unsafe initial backfill default"
    stage_def = next(n for n in ast.walk(trees["models/crm_stage.py"]) if isinstance(n, ast.ClassDef))
    assert any(isinstance(n, ast.FunctionDef) and n.name == "default_get" for n in stage_def.body)
    lead_call = field_call(trees["models/crm_lead.py"], "stage_id")
    assert next(ast.literal_eval(kw.value) for kw in lead_call.keywords if kw.arg == "check_company") is True
    model_domain = next(ast.literal_eval(kw.value) for kw in lead_call.keywords if kw.arg == "domain")

    xml_files = list(ROOT.rglob("*.xml"))
    view_count = 0
    selector_count = 0
    record_ids = set()
    form_domain = None
    team_domain = None
    for path in xml_files:
        tree = etree.parse(str(path))
        for rec in tree.xpath("//record"):
            assert rec.get("id") not in record_ids
            record_ids.add(rec.get("id"))
            if rec.get("model") != "ir.ui.view":
                continue
            view_count += 1
            inherit_id = rec.find("field[@name='inherit_id']").get("ref")
            assert inherit_id in FIXTURES, inherit_id
            source = etree.fromstring(FIXTURES[inherit_id].encode())
            for xp in rec.xpath("field[@name='arch']/xpath"):
                selector = xp.get("expr")
                assert "@string" not in selector, "Translated attributes are forbidden selectors"
                targets = source.xpath(selector)
                assert len(targets) == 1, (inherit_id, selector, len(targets))
                target = targets[0]
                selector_count += 1
                position = xp.get("position")
                if position == "attributes":
                    for attr in xp:
                        target.set(attr.get("name"), attr.text.strip())
                        if attr.get("name") == "domain":
                            ast.parse(attr.text.strip(), mode="eval")
                            if target.get("name") == "stage_id":
                                form_domain = attr.text.strip()
                            elif target.get("name") == "team_ids":
                                team_domain = attr.text.strip()
                elif position in {"before", "after"}:
                    parent = target.getparent()
                    index = parent.index(target) + (position == "after")
                    for child in xp:
                        parent.insert(index, deepcopy(child))
                        index += 1
                elif position == "inside":
                    for child in xp:
                        target.append(deepcopy(child))
                else:
                    raise AssertionError(position)
            if inherit_id == "crm.crm_stage_form":
                company = source.xpath("//field[@name='company_id']")
                assert len(company) == 1 and company[0].getnext().get("name") == "team_ids"
            if inherit_id == "crm.crm_case_kanban_view_leads":
                assert source.xpath("//kanban/field[@name='company_id']")

    assert form_domain and team_domain
    domain_cases = 0
    for company in [False, 10, 20]:
        for team in [False, 100, 200]:
            md = expression(model_domain, company_id=company, team_id=team)
            vd = expression(form_domain, company_id=company, team_id=team)
            assert md == vd
            for stage_company in [False, 10, 20, 30]:
                for stage_teams in [[], [100], [200], [100, 200], [300]]:
                    record = {"company_id": stage_company, "team_ids": stage_teams}
                    expected = (not stage_company or stage_company == company) and (
                        not stage_teams or team in stage_teams
                    )
                    assert matches(md, record) == expected
                    assert matches(vd, record) == expected
                    domain_cases += 1
    team_cases = 0
    for company in [False, 10, 20]:
        domain = expression(team_domain, company_id=company)
        for team_company in [False, 10, 20, 30]:
            assert matches(domain, {"company_id": team_company}) == (
                not company or not team_company or company == team_company
            )
            team_cases += 1

    rule = etree.parse(str(ROOT / "security/crm_stage_security.xml")).xpath("//record")[0]
    assert rule.find("field[@name='groups']") is None, "Company rule must be global"
    assert rule.find("field[@name='model_id']").get("ref") == "crm.model_crm_stage"
    rule_text = rule.find("field[@name='domain_force']").text
    rule_cases = 0
    for selected in [[10], [20], [10, 20], [20, 10]]:
        domain = expression(rule_text, company_ids=selected)
        for owner in [False, 10, 20, 30]:
            assert matches(domain, {"company_id": owner}) == (not owner or owner in selected)
            rule_cases += 1
    for mode in ["read", "write", "create", "unlink"]:
        assert rule.find(f"field[@name='perm_{mode}']").get("eval") == "True"

    with (ROOT / "i18n/tr.po").open("rb") as fh:
        catalog = read_po(fh, locale="tr", abort_invalid=True)
    assert not list(catalog.check())
    write_mo(BytesIO(), catalog)
    for filename in ["models/crm_stage.py", "models/crm_lead.py", "models/crm_team.py", "hooks.py"]:
        for node in ast.walk(trees[filename]):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_":
                msg = ast.literal_eval(node.args[0])
                assert msg in catalog and catalog[msg].string, (filename, msg)
    assert catalog["Company"].string == "Şirket"

    odoo_test_count = sum(
        isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        for node in ast.walk(trees["tests/test_stage_company.py"])
    )
    assert odoo_test_count == 38
    group = next(n for n in ast.walk(trees["models/crm_lead.py"]) if isinstance(n, ast.FunctionDef) and n.name == "_read_group_stage_ids")
    assert len(group.args.args) == 3
    source = (ROOT / "models/crm_lead.py").read_text()
    assert ("from odoo.fields import Domain" in source) is True
    result = {
        "version": "19.0",
        "description_html_safety": "PASS",
        "version_specific_api_signature": "PASS",
        "static_status": "PASS",
        "python_files_parsed_and_compiled": len(py_files),
        "xml_files_parsed": len(xml_files),
        "inherited_views_checked_against_structural_fixtures": view_count,
        "xpath_selectors_checked": selector_count,
        "lead_stage_domain_cases": domain_cases,
        "team_domain_cases": team_cases,
        "company_rule_domain_cases": rule_cases,
        "turkish_translation_messages": len(catalog),
        "odoo_integration_tests_provided": odoo_test_count,
        "odoo_integration_tests_executed": 0,
        "live_or_staging_installation_executed": False,
        "scope": "Static checks only, NOT Odoo ORM/UI/integration execution",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    main()
