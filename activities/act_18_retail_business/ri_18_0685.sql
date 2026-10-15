/*---
indicator_id: RI_18_0685
name_mn: "Дебит картыг шинээр борлуулсан хувь /амжилттай холбогдсон тоо/"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "ДБГ-КХ"
required_info: "Нэгжийн мэдээлэл"
method: |
  Зорилтот харилцагчид борлуулсан картын тоо - Борлуулалтын гүйцэтгэлийн хувийг тооцохдоо амжилттай холбогдсон тооноос тооцно.
  /СЕС програмын тайлангаар баталгаажна/
period_text: "Хамгийн сүүлд авсан шалгалтын дүн"
period: latest                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
