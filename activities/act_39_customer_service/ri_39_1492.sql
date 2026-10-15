/*---
indicator_id: RI_39_1492
name_mn: "Шийдвэрлэгдээгүй гомдлын тоо өсөх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Шийдвэрлэгдээгүй гомдол байхгүй.
  2-1-5 гомдол
  3-6-10 гомдол
  4-11-15 гомдол
  5-15-с дээш гомдол
source_system: "ХДХХ"
required_info: "Шийдвэрлэгдээгүй гомдлын мэдээлэл"
method: "1 сараас дээш хугацаанд шийдвэрлэгдээгүй байгаа гомдлын тоонд үндэслэн үнэлнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
