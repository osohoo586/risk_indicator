/*---
indicator_id: RI_35_1324
name_mn: "Зээлийн судалгааны нэгжид судалгаа хийгдэлгүй олгосон зээл байгаа эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.39                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Зөрчил гараагүй
  2-1 удаагийн зөрчил гарсан
  3-1-5 удаагийн зөрчил гарсан
  4-5-10 удаагийн зөрчил гарсан
  5-10-аас дээш удаагийн зөрчил гарсан
source_system: "ЗГ - МХ"
required_info: "ЗГ, БПМГ-т судлагдах ёстой зээл, кредит картыг салбар судалж олгосон эсэхийг хянасан үр дүн"
method: "Зөрчил гарсан эсэхийг харгалзан үнэлнэ."
period_text: "Сүүлийн 1 жил"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
