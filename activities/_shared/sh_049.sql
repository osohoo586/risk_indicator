/*---
indicator_id: SH_049
name_mn: "Картын системийн тасралт өндөр байх"
manual: true                    # хүн үнэлнэ (ri.py manual). SQL бичвэл бүх үйл ажиллагаанд автомат: manual-ийг хасаад доор нь SQL
status: TODO
version: 0.1.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  5-Монгол банкны шалгуурыг зөрчсөн /долоо хоногт 10 минут/
  3-Банкны KPI-д заасан шалгуурыг зөрчсөн /7 хоногт 11 минут/
  1-Тасралт гараагүй
source_system: "МТАДАХ"
required_info: "Зайны аудитын тайлан"
method: "МТАДАХ-ийн зайны аудитын үр дүнд үндэслэн дүгнэнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
