/*---
indicator_id: RI_34_1297
name_mn: "Хаагдсан төслүүдийн чанарын даалгаварын биелэлтийн хувь"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-79% хүртэл
  4-80-84%
  3-85-90%
  2-90-94%
  1-95-100%
source_system: "ДШГ-ТУХ"
required_info: "Төслийн чанарын биелэлт"
method: "Хаагдсан төслүүдийн чанарын биелэлтийн хувьд үндэслэн үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
