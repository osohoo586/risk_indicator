/*---
indicator_id: RI_22_0822
name_mn: "Гэрээнд заасан ковенантуудыг мөрдөхгүй байх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5- +200%-с дээш, -200% доош
  4- +200%-тай тэнцүү, -200%-тай тэнцүү
  3- +190 < > -190
  2- +180 < > -180
  1- +170 < > -170
source_system: "ХОХХ"
required_info: "Нэгжээс ирүүлсэн мэдээлэл"
method: "ХОХХ-с гэрээ, контракад заасан ковенант нөхцөл мөрдөөгүй жагсаалтад үндэслэнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
