/*---
indicator_id: SH_045
name_mn: "Стандарт хугацаанаас хэтрүүлж хянасан зээлийн гүйлгээ"
manual: true                    # хүн үнэлнэ (ri.py manual). SQL бичвэл бүх үйл ажиллагаанд автомат: manual-ийг хасаад доор нь SQL
status: TODO
version: 0.1.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  1-0-59%
  2-60-69%
  3-70-79%
  4-80-89%
  5-90-100%
source_system: "BI"
required_info: "TXA2020 Хугацаа хоцорч хянасан гүйлгээний дэлгэрэнгүй тайлан"
method: "Хугацаа хоцорч хянасан зээлийн гүйлгээний үр дүнгээр үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
