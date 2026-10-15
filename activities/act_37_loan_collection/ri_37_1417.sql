/*---
indicator_id: RI_37_1417
name_mn: "Зээл барагдуулалтын зардлын төсөв хэтрэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Төсөв 3%-аас дээш хэтэрсэн
  4-Төсөв 3%-аар хэтэрсэн
  3-Төсөв 2%-аар хэтэрсэн
  2-Төсөв 1%-аар хэтэрсэн
  1-Төсөв хэтрээгүй
source_system: "ТАХ"
required_info: "Зардлын зарцуулалтын мэдээлэ"
method: "Зардал хэтэрсэн эсэхэд үндэслэн үнэлнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
