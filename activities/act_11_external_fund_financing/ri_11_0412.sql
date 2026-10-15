/*---
indicator_id: RI_11_0412
name_mn: "Нийт идэвхтэй харилцагчийн тоо - ГХС,ГЭҮЗ"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "ХБСХ"
required_info: "Төлөвлөгөөний биелэлтийн хувь"
method: "Идэвхтэй CIF-тэй ГХС/ГЭҮЗ харилцагчдын тоо (Тайлант хугацаанд ГХС/ГЭҮЗ үйлчилгээтэй байгаа харилцагч)"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
