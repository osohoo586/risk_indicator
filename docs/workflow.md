# Ажлын дараалал (GitLab)

## Дүрэм
1. Нэг activity-г нэг хүн (owner) хийнэ. Бусдын `activities/act_NN_*` folder-т файл засахгүй.
2. Branch = 1 activity, 5–15 үзүүлэлт, 5 хоногоос урт амьдрахгүй.
3. `main` руу шууд push хийхгүй. Merge request (MR) + reviewer-ийн approve заавал.
4. `ri_runner/`, `config/`, `ddl/`, `templates/`, `shared/`-ийн өөрчлөлтийг тусдаа MR-ээр хийж, бусдад мэдэгдэнэ.
   `shared/`, `activities/_shared/` олон үзүүлэлтэд нөлөөлнө: засахаас өмнө ашигладаг үзүүлэлтүүдийг
   (`grep -rn "shared.нэр" activities/`, `python ri.py run --env dev activities/_shared/sh_007.sql -p ...`) dev дээр
   ажиллуулж, `python ri.py verify`-аар шалгана. Master-ийн хэсгийг (жин, шатлал) файлд гараар засахгүй.
5. `python ri.py check` алдаатай, dev дээр ажиллуулаагүй үзүүлэлтэд `status: REVIEW` тавихгүй.

## Branch, commit
```
feature/act_40-ri_40_1525-1530      шинэ үзүүлэлтүүд
fix/sh_007-transfer-not-separation  засвар
chore/runner-...                    runner, config
```
```
feat(ri_40_1525): selection lead time since audit
fix(sh_007): transfers are not separations
```

## Status
| Status | Хэн | Хэзээ |
|---|---|---|
| TODO | — | `python ri.py new`-ээр үүсэхэд |
| IN_PROGRESS | owner | Ажиллаж эхлэхэд |
| REVIEW | owner | MR нээхийн өмнө (check + dev run амжилттай) |
| TESTED | owner | Test орчинд `--test-dates` амжилттай, reviewer зөвшөөрсөн |
| DONE | owner | Prod-д гарсны дараа |

Status-ийг `python ri.py status RI_40_1525 REVIEW --env dev`-ээр солино (сүүлийн run амжилттай эсэхийг шалгана) — MR-тэй хамт commit.

## Өдөр бүр
**Өглөө**
```bash
git switch main && git pull
git switch -c feature/act_40-ri_40_1525-1530   # эсвэл өмнөх branch: git switch ... && git rebase main
```

**Үзүүлэлт бүр**
1. `python ri.py status RI_40_1525` хаана байгааг хэлнэ: ганц бол `activities/act_40_*/ri_40_1525.sql`, олон үйл
   ажиллагаанд давтагддаг бол нийтлэг тодорхойлолт `activities/_shared/sh_NNN.sql` (тусдаа MR — бүх үйл ажиллагаанд
   тусна; [dedup.md](dedup.md)). Эсвэл `/new-indicator`
2. `manual: true`-г хасаж `# ── Тооцоолол ──`: `description`, `connection`, `test_dates`, `status: IN_PROGRESS`
3. Доор нь SQL бичнэ ([sql_standard.md](sql_standard.md))
4. `python ri.py test RI_40_1525 --env dev` (check → dry-run → run → show)
5. `show` / `--save-csv`-ээр 2–3 SOL-ийг хуучин тайлантай гараар тулгана, `python ri.py verify ...`
6. `git commit -m "feat(ri_40_1525): ..."`

**Өдрийн эцэст**
```bash
git push -u origin feature/act_40-ri_40_1525-1530
```
Дууссан үзүүлэлтүүдийг `status: REVIEW` болгоод GitLab-д MR нээнэ (template автоматаар гарна).

**Review (reviewer, өдөрт нэг удаа)**
- MR-ийн checklist-ийг шалгана.
- Өөрөө `python ri.py test RI_.. --env dev` ажиллуулж үр дүнг харна.
- Асуудалгүй бол Approve → Merge (squash). Засвар хэрэгтэй бол MR дээр comment үлдээнэ.

## 7 хоног бүр
| Өдөр | Ажил |
|---|---|
| Даваа | 15 мин уулзалт: `python ri.py progress` — хэд дууссан, энэ 7 хоногт хэдийг хийх, саад |
| Мягмар–Пүрэв | Хөгжүүлэлт, review |
| Баасан | `main`-ийг test орчинд: `python ri.py run --env test -a 1006 --test-dates`, `verify`. Амжилттайг `TESTED` болгох MR |

## Prod руу гаргах
1. `TESTED` үзүүлэлтүүдтэй `main`-д tag тавина: `git tag v2026.10.0 && git push --tags`
2. Prod серверт: `cd /opt/risk_indicators && git fetch --tags && git checkout v2026.10.0`
3. Airflow DAG ([deploy/airflow_dag.py](../deploy/airflow_dag.py)) өдөр бүр `ri.py auto --env prod --all` —
   шинэ / өөрчлөгдсөн үзүүлэлтийг өөрөө ажиллуулна (гараар: `python ri.py run --env prod --all -p 2026-Q3`)
4. Амжилттайг `DONE` болгох MR
5. Алдаа гарвал: `python ri.py retry --env prod --run-id <id>`
6. Буруу утга бичигдсэн бол SQL-ээ засна — маргаашийн `auto` ӨӨРЧЛӨГДСӨН гэж дахин ажиллуулна; хуучин мөр
   `ri_history`-д үлдэнэ.

## Хоёр хүн нэг файл засах шаардлага гарвал
Эхлээд owner-той ярилцана. Owner өөрийн branch-аа merge хийсний дараа нөгөө нь `git pull` хийж засна.
