/*---
indicator_id: RI_03_0105
name_mn: "NSFR"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-100%-аас доош
  4-100-105%
  3-105-110%
  2-110-115%
  1-115%-аас дээш
source_system: "ЭУГ-ЗЗЭУХ, ДАГ-ЗАЧБХ"
required_info: "PR-тайлан, Хугацаа хоцрогдолтой тохиолдолд СУГ-ын метрик үзүүлэлтээр үнэлж болно."
method: |
  Одоо байгаа тогтвортой санхүүжилтийн дүн/ цаашид шаардагдах тогтвортой
  санхүүжилтийн дүнд харьцуулна.
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
