#!/usr/bin/env bash
# Local орчныг (--env local) нэг тушаалаар бэлдэнэ: Docker Oracle + ClickHouse, стандарт банкны demo DB, үр дүнгийн
# хүснэгт.
#
#   ./tests/local/setup.sh              бэлдэнэ (container байхгүй бол үүсгэнэ, унтарсан бол асаана)
#   ./tests/local/setup.sh --reset      үр дүнгийн database (risk_assessment_local)-ийг устгаад шинээр үүсгэнэ
#
# Дараа нь (run.md):
#   python ri.py run    --env local --all -p 2026-Q3                       # ClickHouse руу бичнэ
#   python ri.py verify --env local --all -p 2026-Q3                       # source ↔ ClickHouse тулгана
#   python tests/local/demo_check.py --no-seed                            # бүтэн урсгал + эталон
set -euo pipefail
cd "$(dirname "$0")/../.." || exit 1

RESET=0
for a in "$@"; do
  case "$a" in
    --reset) RESET=1 ;;
    -h|--help) sed -n 2,12p "$0"; exit 0 ;;
    *) echo "Үл мэдэх сонголт: $a (--reset)"; exit 2 ;;
  esac
done

CH_IMAGE=clickhouse/clickhouse-server:25.8
ORA_IMAGE=gvenzl/oracle-free:23.26.3-slim-faststart
CH_PASSWORD="${LOCAL_CH_PASSWORD:-risk_dev}"        # config/local.yaml-ийн default-тай ижил
ORA_PASSWORD=oracle_dev

BOLD=$'\033[1m'; CYAN=$'\033[36m'; GREEN=$'\033[32m'; OFF=$'\033[0m'
step() { printf '\n%s▶ %s%s\n' "$BOLD$CYAN" "$1" "$OFF"; }
ok()   { printf '%s  ✔ %s%s\n' "$GREEN" "$1" "$OFF"; }

# ── 1. Python ─────────────────────────────────────────────────────────────────
step "Python орчин (.venv)"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements-dev.txt
fi
PY=.venv/bin/python
ok "$($PY --version)"

# ── 2. Docker ─────────────────────────────────────────────────────────────────
step "Docker"
if ! docker info >/dev/null 2>&1; then
  [ "$(uname)" = Darwin ] && open -a Docker
  for _ in $(seq 1 60); do docker info >/dev/null 2>&1 && break; sleep 3; done
fi
docker info >/dev/null 2>&1 || { echo "Docker ажиллахгүй байна — Docker Desktop-оо асаана уу"; exit 1; }
ok "Docker ажиллаж байна"

container() {   # container <нэр> <docker run-ийн аргументууд...>: байхгүй бол үүсгэнэ, унтарсан бол асаана
  local name=$1; shift
  if docker ps -a --format '{{.Names}}' | grep -qx "$name"; then
    docker start "$name" >/dev/null
  else
    echo "  $name үүсгэж байна (анх удаа image татна)..."
    docker run -d --name "$name" "$@" >/dev/null
  fi
}

step "ClickHouse (risk-clickhouse, localhost:8123)"
container risk-clickhouse -p 8123:8123 -p 9000:9000 -e CLICKHOUSE_USER=default \
  -e CLICKHOUSE_PASSWORD="$CH_PASSWORD" -e CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1 -e TZ=Asia/Ulaanbaatar \
  --ulimit nofile=262144:262144 "$CH_IMAGE"
for _ in $(seq 1 60); do curl -s -m 2 localhost:8123/ping | grep -q Ok && break; sleep 2; done
curl -s -m 2 localhost:8123/ping | grep -q Ok || { echo "ClickHouse хариу өгөхгүй: docker logs risk-clickhouse"; exit 1; }
ok "ClickHouse бэлэн"

step "Oracle (risk-oracle, localhost:1521/FREEPDB1)"
container risk-oracle -p 1521:1521 -e ORACLE_PASSWORD="$ORA_PASSWORD" "$ORA_IMAGE"
for _ in $(seq 1 100); do
  [ "$(docker inspect -f '{{.State.Health.Status}}' risk-oracle 2>/dev/null)" = healthy ] && break
  sleep 3
done
[ "$(docker inspect -f '{{.State.Health.Status}}' risk-oracle)" = healthy ] || {
  echo "Oracle бэлэн болсонгүй: docker logs risk-oracle"; exit 1; }
ok "Oracle бэлэн"

# ── 3. Seed ───────────────────────────────────────────────────────────────────
step "Стандарт банкны demo DB (COREMIS, FINACLE, ERP, CARDZONE, JIRA + ClickHouse cardzone_dwh)"
$PY tests/local/seed_bank.py
ok "Seed дууслаа"

# ── 4. Үр дүнгийн хүснэгт ─────────────────────────────────────────────────────
ENV=local
step "Үр дүнгийн хүснэгт (--env $ENV)"
if [ "$RESET" = 1 ]; then
  $PY - "$ENV" <<'PYEOF'
import sys
from ri_runner.config import EnvConfig
from ri_runner.db import connect
cfg = EnvConfig(sys.argv[1])
with connect(cfg, cfg.result_connection) as ch:
    ch.execute(f"DROP DATABASE IF EXISTS `{cfg.result_db}` SYNC")
print(f"  {cfg.result_db} устгалаа")
PYEOF
fi
$PY ri.py init-db --env "$ENV"

step "Бүх DB"
$PY tests/local/show_dbs.py --env "$ENV"

cat <<EOF

${BOLD}Бэлэн. Одоо:${OFF}
  $PY ri.py run    --env $ENV --all -p 2026-Q3                          # 35 үйл ажиллагааны автомат үзүүлэлт
  $PY ri.py verify --env $ENV --all -p 2026-Q3                          # source ↔ ClickHouse
  $PY tests/local/demo_check.py --no-seed                               # бүтэн урсгал + эталон → output/demo_report.html
Дэлгэрэнгүй: run.md
EOF
