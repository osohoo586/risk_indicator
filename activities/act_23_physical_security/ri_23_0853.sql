/*---
indicator_id: RI_23_0853
name_mn: "Онцгой байдлын газар болон холбогдох байгууллагаас тавьсан шаардлагын хэрэгжилт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Шаардлагыг хэрэгжүүлээгүй
  4-Шаардлагын хэрэгжилт 70-79%
  3-Шаардлагын хэрэгжилт 80-89%
  2-Шаардлагын хэрэгжилт 90-99%
  1-Шаардлагыг бүрэн хэрэгжүүлсэн./Шаардлага ирээгүй/
source_system: "АБХ"
required_info: "Онцгой байдлын газраас ирүүлсэн шаардлага"
method: "ОБГ-аас ирүүлсэн шаардлагын хэрэгжилтилтэд үндэслэн дүгнэнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
