/*---
indicator_id: RI_04_0158
name_mn: "Урьдчилсан захиалгат арилжаа; \"Алтны форвард арилжаа\" гэрээ байгуулсан харилцагчийн тоо"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "Харилцагчтай байгуулсан хэлцлийн тоогоор гүйцэтгэлийг тооцно."
required_info: "Нийт гэрээ, хэлцлийн тоо"
method: "Төлөвлөгөөний биелэлтэд үндэслэн үнэлнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
