/*---
indicator_id: RI_21_0788
name_mn: "Автоматжуулж, сайжруулсан ажлын тоо"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  0-Үнэлэхгүй
  1-96.1-100%
  2-92.1-96%
  3-89.1-92%
  4-85-89%
  5-85% - с доош
  1-Хэмнэсэн хүн/цаг өссөн. Зорилтод хүрсэн
source_system: "ДШГ-ПУХ"
required_info: "Сайжруулж байгаа ажлын мэдээлэл"
method: |
  Дата суурилсан бүтээгдэхүүн, дашбоард, сервис шинээр нэвтрүүлэх
  Шинээр хөгжүүлсэн бүтээгдэхүүний алгоритм, платформ, сервисийн тоо
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
