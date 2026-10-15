/*---
indicator_id: RI_02_0060
name_mn: "Төслүүдтэй хамтарч ажилласан байдал"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Хамрах хугацаанд төсөл хөтөлбөрт санал хүргүүлээгүй.
  1-Хамрах хугацаанд төсөлд оролцох санал хүргүүлсэн.
source_system: "ЖДБГ-БХХ"
required_info: "Төслийн мэдээлэл, хүргүүлсэн санал"
method: "ЗГ, МБ-аас хэрэгжүүлж буй төсөлд оролцож, санал хүргүүлсэн байдлаар нэгжээс ирүүлсэн мэдээллээр үнэлнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
