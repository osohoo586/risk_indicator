/*---
indicator_id: RI_20_0755
name_mn: "Хүсэлт шийдэх дундаж хугацаа -\nАТМ, CDM-д хүрч очих"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "БТГ-АТМ алба"
required_info: "Аналитик датамайнингийн дашбаорд"
method: |
  Аналитик датамайнингийн дашбаорд-с гүйцэтгэлийг гаргана. - Тайлан татаж ирүүлнэ.
  Хугацааны зорилт: 1 цаг 20 минут
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
