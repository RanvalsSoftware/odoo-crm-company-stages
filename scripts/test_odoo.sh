#!/usr/bin/env bash
# Disposable integration runner. Never point this script at a production database.
set -Eeuo pipefail
version="${1:-}"
case "$version" in 17.0|18.0|19.0) ;; *) echo 'Usage: bash scripts/test_odoo.sh 17.0|18.0|19.0' >&2; exit 2;; esac
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v docker >/dev/null || { echo 'Docker is required.' >&2; exit 2; }
command -v python3 >/dev/null || { echo 'Python 3 is required.' >&2; exit 2; }
python3 - "$root" "$version" <<'PY'
import ast, pathlib, sys
root, version = pathlib.Path(sys.argv[1]), sys.argv[2]
manifest = root / 'crm_company_stages' / '__manifest__.py'
if not manifest.is_file():
    raise SystemExit('Run from the matching version branch, not the main/site branch.')
data = ast.literal_eval(manifest.read_text())
if not data['version'].startswith(version + '.'):
    raise SystemExit('The checkout does not match the requested Odoo version.')
PY
docker info >/dev/null
suffix="$(python3 -c 'import secrets; print(secrets.token_hex(6))')"
network="crm-stage-qa-${suffix}"
pg="${network}-pg"
app="${network}-odoo"
password="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
created_network=0
created_pg=0
created_app=0
cleanup() {
    if [[ "$created_app" == 1 ]]; then docker rm -f -v "$app" >/dev/null 2>&1 || true; fi
    if [[ "$created_pg" == 1 ]]; then docker rm -f -v "$pg" >/dev/null 2>&1 || true; fi
    if [[ "$created_network" == 1 ]]; then docker network rm "$network" >/dev/null 2>&1 || true; fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mkdir -p "$root/test-results"
log="$root/test-results/odoo-${version}.log"
# No host ports or existing volumes/databases are used.
docker network create --label crm-company-stages-qa=true "$network" >/dev/null
created_network=1
docker run -d --name "$pg" --network "$network" \
    --label crm-company-stages-qa=true \
    -e POSTGRES_DB=postgres -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD="$password" \
    postgres:16 >/dev/null
created_pg=1
ready=0
for _ in $(seq 1 60); do
    if docker exec "$pg" pg_isready -U odoo -d postgres >/dev/null 2>&1; then ready=1; break; fi
    sleep 1
done
if [[ "$ready" != 1 ]]; then docker logs "$pg" >&2; echo 'PostgreSQL did not become ready.' >&2; exit 1; fi
# Set the flag before run so a failing/stopped app container is cleaned up too.
created_app=1
docker run --name "$app" --network "$network" \
    --label crm-company-stages-qa=true \
    -e HOST="$pg" -e USER=odoo -e PASSWORD="$password" \
    --mount "type=bind,src=$root/crm_company_stages,dst=/mnt/extra-addons/crm_company_stages,readonly" \
    "odoo:${version}" odoo \
    -d crm_stages_disposable -i crm_company_stages \
    --test-enable --test-tags /crm_company_stages \
    --stop-after-init --without-demo=all --http-port=8069 \
    --limit-time-cpu=1200 --limit-time-real=2400 \
    --log-handler=odoo.addons.crm_company_stages.tests:INFO \
    2>&1 | tee "$log"
# Fail closed when test discovery cannot be confirmed; inspect the log on failure.
if ! grep -q 'test_38_expanded_columns_do_not_elevate_access' "$log"; then
    echo 'The final addon test was not found in the log. Check test discovery before accepting this run.' >&2
    exit 1
fi
if grep -Eq 'FAIL:|ERROR:|[1-9][0-9]* failed,|[1-9][0-9]* error\(s\)' "$log"; then
    echo 'A test failure was reported. Inspect the complete log.' >&2
    exit 1
fi
echo "Run completed for ${version}. Review $log and perform browser smoke tests."
