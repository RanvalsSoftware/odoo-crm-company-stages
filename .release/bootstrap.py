#!/usr/bin/env python3
"""Rebuild the reviewed release, then publish only after all three CI jobs pass.

The four source chunks are an XZ-compressed, content-deduplicated UTF-8 snapshot.
Every decoded file is SHA-256 checked before writing. No credentials are embedded.
"""
from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
import lzma
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

VERSIONS = ("17.0", "18.0", "19.0")
MODULE = "crm_company_stages"
REPOSITORY = "RanvalsSoftware/odoo-crm-company-stages"
URL = "https://github.com/" + REPOSITORY
SNAPSHOT_SHA256 = "a8a616fca1a9137f5db31d80427bfa540887bfd6e1927dbd9ccc99ff299757a6"
SEED = Path(__file__).resolve().parent


def run(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(args, cwd=cwd, check=True, text=True, stdout=subprocess.PIPE)
    if result.stdout:
        print(result.stdout, end="", flush=True)
    return result.stdout.strip()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def safe_path(root: Path, relative: str) -> Path:
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative or not path.parts:
        raise ValueError("Unsafe source path: " + relative)
    return root.joinpath(*path.parts)


def decode(destination: Path) -> None:
    encoded = "".join((SEED / f"source.{i:02d}.b64").read_text().strip() for i in range(4))
    compressed = base64.b64decode(encoded, validate=True)
    if hashlib.sha256(compressed).hexdigest() != SNAPSHOT_SHA256:
        raise ValueError("Source snapshot checksum mismatch")
    payload = json.loads(lzma.decompress(compressed))
    for relative, digest in payload["files"].items():
        text = payload["blobs"][digest]
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != digest:
            raise ValueError("Source file checksum mismatch: " + relative)
        write(safe_path(destination, relative), text)
    # Any later, human-readable CI fixes must replace an existing snapshot file.
    overrides = SEED / "overrides"
    if overrides.is_dir():
        for patch in sorted(overrides.rglob("*")):
            if patch.is_file():
                relative = patch.relative_to(overrides).as_posix()
                if relative not in payload["files"]:
                    raise ValueError("Override does not match an original file: " + relative)
                write(safe_path(destination, relative), patch.read_text(encoding="utf-8"))
    print(f"Verified {len(payload['files'])} source files.", flush=True)


def render(source: Path, assets: Path) -> None:
    from playwright.sync_api import sync_playwright
    assets.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.environ.get("CRM_CHROMIUM_PATH"))
        page = browser.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=1)
        page.set_content((source / "presentation/cover.html").read_text())
        page.wait_for_function("document.querySelectorAll('.column').length >= 3")
        page.screenshot(path=str(assets / "cover.png"))
        page.locator(".visual").screenshot(path=str(assets / "workflow.png"))
        page.set_viewport_size({"width": 256, "height": 256})
        page.set_content((source / "presentation/icon.html").read_text())
        page.screenshot(path=str(assets / "icon.png"))
        browser.close()


def make_zip(addon: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(addon.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            entry = zipfile.ZipInfo(path.relative_to(addon.parent).as_posix(), (2026, 9, 9, 0, 0, 0))
            entry.external_attr = 0o100644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, path.read_bytes())


def build(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="crm-source-") as temp:
        source = Path(temp)
        decode(source)
        main = output / "main"
        main.mkdir()
        for name in ("README.md", "README_TR.md", "PUBLISH_TR.md", "QA_OVERVIEW_TR.md", "SOURCE_REVIEW.md", "LICENSE", "COPYING", "NOTICE"):
            shutil.copy2(source / name, main / name)
        readme = (main / "README.md").read_text()
        readme = readme.replace("../../tree/", URL + "/tree/").replace("../../actions", URL + "/actions")
        write(main / "README.md", readme)
        shutil.copytree(source / "presentation", main / "presentation")
        assets = main / "presentation"
        render(source, assets)
        shutil.copytree(source / "website", main / "docs")
        page = (main / "docs/index.html").read_text()
        page = page.replace("<strong>Release preparation build · 9 September 2026.</strong> Odoo/PostgreSQL runtime tests have not been run in this preparation environment. Validate in staging before production. The Odoo Apps listing is not yet published.", "<strong>Free community release.</strong> Version branches are published only after their Odoo/PostgreSQL integration checks pass. See the repository Actions and VALIDATION.md for the tested commits. Validate your own installation in staging before production. Odoo Apps submission is a separate step.")
        page = page.replace("Runtime tests still need to be executed in a disposable Odoo/PostgreSQL database.", "The publication workflow runs these tests in disposable Odoo/PostgreSQL databases; inspect the repository Actions for results.")
        write(main / "docs/index.html", page)
        zip_hashes = []
        for version in VERSIONS:
            target = output / "versions" / version
            shutil.copytree(source / "versions" / version, target)
            addon = target / MODULE
            manifest = ast.literal_eval((addon / "__manifest__.py").read_text())
            assert manifest["version"].startswith(version + ".")
            assert manifest.get("price", 0) == 0 and manifest["depends"] == ["crm"]
            for image in ("cover.png", "workflow.png", "icon.png"):
                shutil.copy2(assets / image, addon / "static/description" / image)
            write(target / "scripts/test_odoo.sh", (source / "scripts/test_odoo.sh").read_text())
            write(target / "README.md", f"# CRM Company Stages — Odoo {version}\n\nFree LGPL-3 addon: `{MODULE}/`.\n\n" + f"[Website source]({URL}/tree/main/docs) · [Validation]({URL}/blob/main/VALIDATION.md) · [Actions]({URL}/actions)\n\n" + "Use this branch only with the matching Odoo version. See the addon README for usage and migration precautions.\n")
            for name in ("LICENSE", "COPYING", "NOTICE"):
                shutil.copy2(source / name, target / name)
            qa = addon / "QA_REPORT_TR.md"
            write(qa, "# İlk hazırlık raporu (tarihsel kayıt)\n\nAşağıdaki rapor ilk hazırlık ortamını anlatır. Daha sonra gerçekleştirilen gerçek Odoo testleri için deponun Actions kayıtlarını ve main/VALIDATION.md dosyasını inceleyin.\n\n" + qa.read_text())
            run(sys.executable, str(addon / "qa/validate_static.py"), cwd=target)
            for cache in addon.rglob("__pycache__"):
                shutil.rmtree(cache)
            destination = main / "docs/downloads" / f"{MODULE}-{manifest['version']}.zip"
            make_zip(addon, destination)
            zip_hashes.append(f"{hashlib.sha256(destination.read_bytes()).hexdigest()}  {destination.name}")
        write(main / "docs/downloads/SHA256SUMS.txt", "\n".join(zip_hashes) + "\n")
    integrity = {path.relative_to(output).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in sorted(output.rglob("*")) if path.is_file()}
    write(output / "build-hashes.json", json.dumps(integrity, indent=2) + "\n")
    print("Prepared all three versions and website.", flush=True)


def publish(output: Path) -> None:
    if os.environ.get("GITHUB_REPOSITORY") != REPOSITORY:
        raise ValueError("Publication is restricted to the requested repository")
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise ValueError("Initial publication must run from main")
    for relative, digest in json.loads((output / "build-hashes.json").read_text()).items():
        if hashlib.sha256(safe_path(output, relative).read_bytes()).hexdigest() != digest:
            raise ValueError("Built artifact checksum mismatch: " + relative)
    repo = Path.cwd()
    base = run("git", "rev-parse", "HEAD", cwd=repo)
    expected = os.environ["GITHUB_SHA"]
    if base != expected:
        raise ValueError("Repository changed after this release was prepared")
    remote_main = run("git", "ls-remote", "origin", "refs/heads/main", cwd=repo).split()[0]
    if remote_main != base:
        raise ValueError("Concurrent main update; refusing to overwrite it")
    for version in VERSIONS:
        if run("git", "ls-remote", "origin", f"refs/heads/{version}", cwd=repo):
            raise ValueError(f"Branch {version} already exists; initial publisher will not overwrite it")
    run_url = URL + "/actions/runs/" + os.environ["GITHUB_RUN_ID"]
    report = ("# Runtime validation\n\n" + f"Integration jobs passed before publication: [workflow run]({run_url}).\n\n"
              + f"Source preparation commit: `{base}`.\n\n"
              + "Odoo 17.0, 18.0 and 19.0 were each installed with CRM Company Stages in disposable Odoo/PostgreSQL containers. The provided 38 addon tests were discovered and checked for each version. All matrix jobs are required to succeed before this report and the branches can be published.\n\n"
              + "Static validation: 552 company/team/domain combinations across the three versions.\n\n"
              + "These are Community runtime checks, not a guarantee for every Enterprise combination or customer customization. Browser smoke tests and backups remain necessary. No production/customer database was used.\n")
    write(output / "main/VALIDATION.md", report)
    run("git", "config", "user.name", "github-actions[bot]", cwd=repo)
    run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com", cwd=repo)
    references = []
    with tempfile.TemporaryDirectory(prefix="crm-publish-") as temp:
        for version in VERSIONS:
            tree = Path(temp) / version
            run("git", "worktree", "add", "--detach", str(tree), base, cwd=repo)
            shutil.copytree(output / "versions" / version, tree, dirs_exist_ok=True)
            write(tree / "VALIDATION.md", report)
            run("git", "add", MODULE, "scripts", "README.md", "LICENSE", "COPYING", "NOTICE", "VALIDATION.md", cwd=tree)
            run("git", "commit", "-m", f"feat: release free CRM Company Stages for Odoo {version}", cwd=tree)
            sha = run("git", "rev-parse", "HEAD", cwd=tree)
            references.append(f"{sha}:refs/heads/{version}")
            run("git", "worktree", "remove", str(tree), cwd=repo)
        shutil.copytree(output / "main", repo, dirs_exist_ok=True)
        run("git", "add", "README.md", "README_TR.md", "PUBLISH_TR.md", "QA_OVERVIEW_TR.md", "SOURCE_REVIEW.md", "LICENSE", "COPYING", "NOTICE", "VALIDATION.md", "docs", "presentation", cwd=repo)
        run("git", "commit", "-m", "docs: publish free CRM Company Stages website and tested version downloads", cwd=repo)
        main_sha = run("git", "rev-parse", "HEAD", cwd=repo)
        # One atomic, non-forced push: any conflict prevents every ref update.
        run("git", "push", "--atomic", "origin", *references, f"{main_sha}:refs/heads/main", cwd=repo)
    print("Published main, 17.0, 18.0 and 19.0. Pages setup and Odoo Apps submission are separate.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("build", "publish"))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    (build if args.mode == "build" else publish)(args.output.resolve())


if __name__ == "__main__":
    main()
