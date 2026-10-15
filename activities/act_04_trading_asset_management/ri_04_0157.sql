/*---
indicator_id: RI_04_0157
name_mn: "Хувьцааны багцын эрсдэлд тохируулсан active өгөөж (IR)"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-0.2 ба түүээс дээш
  5-0.2-өөс бага
source_system: "НУГ-АХ"
required_info: "АПУХ-ийн үнэлгээ"
method: "Хувьцааны багцын гүйцэтгэлийг тооцон, ОУ-н хувьцаа, дотоодын дилерийн баримталдаг менежменттэй дөхсөн бенчмарк индекстэй харьцуулсан коэффициентээр гүйцэтгэлийг тооцно."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
