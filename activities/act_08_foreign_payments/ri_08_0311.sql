/*---
indicator_id: RI_08_0311
name_mn: "АТМ-н тасралтгүй ажиллагаа ДТТХ-ДГМА"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Тасралт гараагүй
  5-Тасралт гарсан
source_system: "БТГ-ДТТХ"
required_info: "Тасралт үүссэн эсэх"
method: "Тухайн нэгжээс хамааран тасарсан минут нь доод хязгаараас давсан тохиолдолд тухайн АТМ-д харгалзах хувийг авах ёстой хувиас хасаж тооцно."
period_text: "Аудит орсноос хойш улирлын дундаж."
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
