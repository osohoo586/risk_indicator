/*---
indicator_id: SH_025
name_mn: "Аудиторын үнэлэмж"
manual: true                    # хүн үнэлнэ (ri.py manual). SQL бичвэл бүх үйл ажиллагаанд автомат: manual-ийг хасаад доор нь SQL
status: TODO
version: 0.1.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score6"
scale_text: |
  1-1
  2-2
  3-3
  4-4
  5-5
source_system: "ДАГ, ХНУГ"
required_info: |
  - Exit meeting
  - Аудиторуудын Rumor мэдээлэл
  - Whistle blow мэдээлэл
method: "Тухайн үйл ажиллагааны эрсдэлийн үнэлгээг хийх багаараа ярилцаж үнэлнэ. Хамгийн сүүлд аудит орсон ажлын хэсэг, эрсдэлийн үнэлгээ хийх багийн үнэлэмж болон exit meeting, rumour бүртгэлийг үндэслэн үнэлнэ. Exit meeting-с мэдээллийн бүртгэлгүй бол 1 оноо, бүртгэгдсэн бол агуулгаас үндэслэн 5 эсвэл 3 оноо өгнө."
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
