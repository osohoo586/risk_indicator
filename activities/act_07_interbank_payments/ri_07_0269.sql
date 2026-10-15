/*---
indicator_id: RI_07_0269
name_mn: "Их  дүнтэй гүйлгээний эрсдэлийн хяналтыг хийж гүйцэтгэсэн байдал"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  Аудит орсноос хойш хугацаанд-0
  -1
  -2
  -3
  -4
  -5
source_system: "БТГ-ТТХ-БХТТA"
required_info: "Хяналтын Excel бүртгэл"
method: "300 сая төгрөгөөс дээш банк хоорондын гүйлгээг хянасан байдлыг харгалзан үнэлнэ. Хянасан гүйлгээ/Хянах гүйлгээ"
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
