/*---
indicator_id: SH_040
name_mn: "Зээлийн шийдвэр гаргалт"
manual: true                    # хүн үнэлнэ (ri.py manual). SQL бичвэл бүх үйл ажиллагаанд автомат: manual-ийг хасаад доор нь SQL
status: TODO
version: 0.1.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  5-Зээл шийдвэрлэх эрхий матриц зөрчиж зээл олгосон
  4-Зээлийн нөхцөл өөрчлөх шийдвэрийг дангаар шийдвэрлэсэн.
  0-Зөрчил гараагүй.
source_system: "Зайны аудит"
required_info: "Зайны аудитын тайлан"
method: "Зайны аудитаар гарсан зөрчилд үндэслэн үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
