/*---
indicator_id: RI_23_0856
name_mn: "Мөнгөн зөөврийн үйл ажиллагааг тогтмол хянаж, зөрчлийг бүртгэлжүүлсэн байдал"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Бүртгэлжүүлээгүй, 6% дээш зөрчил илэрсэн
  4-Нийт зөөврийн 5-6%-д зөрчил илэрсэн
  3-Нийт зөөврийн 3-4%-д зөрчил илэрсэн
  2-Нийт зөөврийн 1-2%-д зөрчил илэрсэн
  1-Асуудал илрээгүй
source_system: "АБХ"
required_info: "ЖИРА бүртгэл"
method: "ЖИРА бүртгэлээс нэг бүрчлэн тоолно. Асуудал илэрсэн эсэхийг баталгаажуулна."
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
