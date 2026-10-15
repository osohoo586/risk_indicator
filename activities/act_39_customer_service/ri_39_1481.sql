/*---
indicator_id: RI_39_1481
name_mn: "Харилцагч, үйлчлүүлэгчийн сэтгэл ханамж буурах."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-z
  3-Харилцагчийн үйлчилгээний сэтгэл ханамжид өөрчлөлт гараагүй.
  1-Сэтгэл ханамжийн судалгааны үр дүн эерэг гарсан буюу өмнөх үеэс сайжирсан.
source_system: "МХ"
required_info: "Сэтгэл ханамжийн судалгаа"
method: "Харилцагч, үйлчлүүлэгчийн сэтгэл ханамжийн судалгааны үр дүнг харгалзах."
period_text: "Өмнөх хагас жилтэй харьцуулна"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
