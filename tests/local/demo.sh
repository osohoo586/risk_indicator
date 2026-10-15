#!/usr/bin/env bash
# Стандарт банкны demo DB дээр алхам алхмаар: бэлтгэл → SQL → check → run (файл, folder, бүгд) → ClickHouse →
# гарын үнэлгээ → verify → тайлан → auto → бүтэн эталон шалгалт.
#
#   ./tests/local/demo.sh              бүгдийг нэг дор
#   ./tests/local/demo.sh --step       алхам бүрийн дараа Enter дарж үргэлжлүүлнэ (уншиж харахад)
#   ./tests/local/demo.sh --no-setup   бэлтгэлийг алгасна (setup.sh өмнө нь хийсэн бол)
#
# Үр дүн risk_assessment_local database-д бичигдэнэ (dev, prod-д хүрэхгүй). Тушаалууд: run.md
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1

PY=.venv/bin/python
STEP=0
SETUP=1
for a in "$@"; do
  case "$a" in
    --step) STEP=1 ;;
    --no-setup) SETUP=0 ;;
    -h|--help) sed -n 2,9p "$0"; exit 0 ;;
    *) echo "Үл мэдэх сонголт: $a (--step, --no-setup)"; exit 2 ;;
  esac
done

BOLD=$'\033[1m'; CYAN=$'\033[36m'; GREEN=$'\033[32m'; YEL=$'\033[33m'; DIM=$'\033[2m'; OFF=$'\033[0m'
N=0
step()  { N=$((N + 1)); printf '\n%s━━━ %d. %s ━━━%s\n' "$BOLD$CYAN" "$N" "$1" "$OFF"; [ -n "${2:-}" ] && printf '%s%s%s\n' "$DIM" "$2" "$OFF"; return 0; }
run()   { printf '%s$ %s%s\n' "$GREEN" "$*" "$OFF"; "$@"; }
must()  { run "$@" || { printf '%s✘ Алдаа гарлаа — дээрх мессежийг харна уу%s\n' "$YEL" "$OFF"; exit 1; }; }
pause() { [ "$STEP" = 1 ] && read -r -p "   ↵ Enter дарж үргэлжлүүлнэ... " _; return 0; }
sql()   { run "$PY" tests/local/ch_query.py "$1"; }

HR=activities/act_40_human_resources
CORP=activities/act_01_corporate_business
DB=risk_assessment_local

# ── Бэлтгэл ───────────────────────────────────────────────────────────────────
if [ "$SETUP" = 1 ]; then
  step "Бэлтгэл: Docker Oracle + ClickHouse, стандарт банкны demo DB, хоосон үр дүнгийн хүснэгт" "./tests/local/setup.sh --reset"
  must ./tests/local/setup.sh --reset
  pause
fi
[ -x "$PY" ] || { echo "Эхлээд ./tests/local/setup.sh"; exit 1; }

# ── SQL ───────────────────────────────────────────────────────────────────────
step "Нийтлэг тооцоолол: 35 үйл ажиллагаанд НЭГ SQL" "SOL бүрийн мөр → үйл ажиллагаа бүр өөрийн SOL-уудаар Σ тоологч / Σ хуваарь"
run cat activities/_shared/sh_007.sql
pause
step "Давхцах хэсэг: shared/erp/sol_flow.sql" "SH_007 (SOL), RI_40_1519, RI_40_1520 (банк нийт) гурвуулаа энэ НЭГ кодыг ашиглана"
run cat shared/erp/sol_flow.sql
pause
step "Хуучин procedure: RI_01_0013" "BEGIN FINACLE.RA_LOAN_PKG.DECISION_SPEED(..., :rc); END; — READ ONLY transaction дотор"
run cat "$CORP/ri_01_0013.sql"
pause

step "Static шалгалт (DB-гүй)" "SQL дүрэм, параметрийн dialect, shared/, жин, шатлал, BRANCHID"
run "$PY" ri.py check --env local
pause

# ── Run ───────────────────────────────────────────────────────────────────────
step "Нэг файл" "Банкны ажилтнуудын эргэц (BANK түвшин, сүүлийн 1 жил)"
must "$PY" ri.py run --env local "$HR/ri_40_1520.sql" -p 2026-Q3
pause
step "Нэг үйл ажиллагаа (folder)" "Хүний нөөц: 4 өөрийн SQL + 8 нийтлэг тооцоолол → нийт оноо"
must "$PY" ri.py run --env local "$HR/" -p 2026-Q2 -p 2026-Q3
pause
step "Бүх үйл ажиллагаа" "303 автомат + 2 нэмэлт (9001+) үзүүлэлт, 35 үйл ажиллагаа"
must "$PY" ri.py run --env local --all -p 2026-Q3
pause

# ── ClickHouse ────────────────────────────────────────────────────────────────
step "ClickHouse: үзүүлэлт бүр (v_risk_indicators)" "branch_id = үйл ажиллагаа, sol_id = түүний SOLID-ууд (MAIN-аас), file_name = эх файл"
sql "SELECT indicator_id, ra_name, branch_id, sol_id, round(scale, 4) AS scale, score, last_workdate
     FROM $DB.v_risk_indicators WHERE branch_id = '1006' AND last_workdate = '2026-09-30' AND source_kind != 'MANUAL'
     ORDER BY indicator_id"
pause
step "SOL задаргаа: RI_40_1545 (SH_007)" ""
run "$PY" ri.py show --env local -i RI_40_1545 -d 2026-09-30
pause

# ── Гарын үнэлгээ ─────────────────────────────────────────────────────────────
step "Гарын үнэлгээ: Excel template" "VALUE / VALUE_TEXT / SCORE баганыг бөглөөд manual load (demo_check жишээ утгаар бөглөнө)"
run "$PY" ri.py manual template -a 1006 --date 2026-09-30
pause

# ── Шалгах ────────────────────────────────────────────────────────────────────
step "verify: source ↔ ClickHouse" "Source дээр дахин тооцоолж мөр бүрээр тулгана (юу ч бичихгүй)"
must "$PY" ri.py verify --env local "$HR/" -p 2026-Q3
pause
step "Үйл ажиллагааны тайлан (HTML)" ""
run "$PY" ri.py report --env local -a 1006 -d 2026-09-30
pause
step "auto: дутуу / хуучирсныг л" "Бүгд бичигдсэн бол ажиллуулах зүйл алга (prod: Airflow өдөр бүр)"
run "$PY" ri.py auto --env local --all --as-of 2026-10-14 --since 2026-07-01 --plan
pause

step "Бүтэн шалгалт: эталон (Python) ↔ ClickHouse, гарын үнэлгээ, алдааны тохиолдлууд" "output/demo_report.html"
must "$PY" tests/local/demo_check.py --no-seed

step "Дууслаа" ""
cat <<EOF
Бүх DB:        $PY tests/local/show_dbs.py
Өөрийн файл:   $PY ri.py run    --env local <файл эсвэл folder> -p 2026-Q3
               $PY ri.py verify --env local <файл эсвэл folder> -p 2026-Q3
Тайлан:        output/demo_report.html, output/report_*.html
Тушаалууд:     run.md
EOF
