/*---
indicator_id: RI_13_0480
name_mn: "Харилцагч, ажилтнуудад хүргэсэн сургалтын үнэлгээ"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "ОУБГ-ТСХ"
required_info: "Нэгжээс ирүүлсэн мэдээлэлд үндэслэнэ."
method: "Харилцагч болон ажилтнуудад орсон сургалтуудыг гүйцэтгэлийн үнэлгээгээр тооцно"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
