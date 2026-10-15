/*---
indicator_id: RI_21_0783
name_mn: "Бизнес процесс хяналтыг хэрэгжүүлэх аргачлалыг тодорхойлсон эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Аргачлалыг тодорхойлсон
  5-Аргачлалыг тодорхойлоогүй.
source_system: "ДШГ-ПУХ"
required_info: "Аргачлалтай болсон эсэх"
method: "Аргачлалтай болсон эсэх"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
