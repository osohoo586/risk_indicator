/*---
indicator_id: SH_042
name_mn: "Банкны стратегид ач холбогдолтой ажил хийгдсэн эсэх"
manual: true                    # хүн үнэлнэ (ri.py manual). SQL бичвэл бүх үйл ажиллагаанд автомат: manual-ийг хасаад доор нь SQL
status: TODO
version: 0.1.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score5"
scale_text: |
  1-Бага
  3-Дунд
  5-Өндөр
source_system: "Нэгжийн тайлан мэдээлэл"
required_info: "Хамрах хугацааны тайлан мэдээлэл"
method: "Үйл ажиллагаатай холбоотой хийгдсэн ажлын Стратегийн ач холбогдлын зэргээр үнэлнэ"
period_text: "Хамрах улирал"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
