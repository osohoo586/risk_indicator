/*---
indicator_id: RI_39_1482
name_mn: "Харилцагчийн үйлчилгээний стандартын хэрэгжилт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-75% ба түүнээс доош
  4-76%-89% боловч өмнөх үеэс бууралттай
  3-76%-89% боловч өмнөх үеэс өсөлттэй
  2-90% ба түүнээс дээш боловч, өмнөх үеэс бууралттай
  1-90% ба түүнээс дээш, өмнөх үеэс өсөлттэй
source_system: "ХТХ"
required_info: "Стандарт хэрэгжилт"
method: "ХҮА-ын стандарт хэрэгжилтийн үр дүнг үндэслэн дүгнэнэ"
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
