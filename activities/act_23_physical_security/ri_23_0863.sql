/*---
indicator_id: RI_23_0863
name_mn: "Дохиоллын системийг идэвхижүүлэхгүй хоносон тохиолдол гарсан эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Зөрчил 10-ээс дээш бүртгэгдсэн
  4-Зөрчил 5-10  бүртгэгдсэн
  3-Зөрчил 1-ээс 5 бүртгэгдсэн
  2-Зөрчил 1 бүртгэгдсэн
  1-Зөрчил гараагүй.
source_system: "СУГ-ТҮХ, МХ-СХА"
required_info: "Төлөвлөгөөний гүйцэтгэл"
method: "ББГ сегментийн зээлийн үлдэгдэл / Системийн нийт байгууллагын (Corp+SME) зээлийн үлдэгдэл"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
