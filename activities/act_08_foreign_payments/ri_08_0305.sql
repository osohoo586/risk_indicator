/*---
indicator_id: RI_08_0305
name_mn: "Ностро байршуулж буй гадаадын банкны рейтинг буурах"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Рейтинг буурсан тохиолдол гарсан
  0-Рейтинг буурсан тохиолдол гараагүй.
source_system: "ОУБГ"
required_info: "Корреспондент банкуудын рейтингийн мэдээлэл"
method: "Эрсдэлээр жигнэсэн активыг өсгөх эрсдэлтэй."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
