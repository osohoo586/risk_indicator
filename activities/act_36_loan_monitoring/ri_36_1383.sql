/*---
indicator_id: RI_36_1383
name_mn: "Зээлийн үйл ажиллагаанд оролцогчдын мэдлэгийн шалгалтын дундаж хувь."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-95-100
  2-90-94
  3-85-89
  4-80-84
  5-80-с доош, аваагүй бол
source_system: "ЗГ-ЗМХ"
required_info: "Мэдлэгийн шалгалтын үр дүн"
method: "Зээлийн үйл ажиллагааны мэдлэгийн шалгалтын үр дүнгийн дундаж үнэлгээгээр үнэлнэ. /Бүх нэгжийн ажилтны дундаж/"
period_text: "Хамгийн сүүлд авсан шалгалтын дүн"
period: latest                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
