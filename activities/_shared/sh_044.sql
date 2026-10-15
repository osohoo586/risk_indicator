/*---
indicator_id: SH_044
name_mn: "Гүйлгээний чанар/ залруулгын гүйлгээ"
manual: true                    # хүн үнэлнэ (ri.py manual). SQL бичвэл бүх үйл ажиллагаанд автомат: manual-ийг хасаад доор нь SQL
status: TODO
version: 0.1.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-1
source_system: "БТГ-ТТХ-БХТТA"
required_info: "Залруулгын гүйлгээний тоо"
method: "Гүйлгээний чанар/ залруулгын гүйлгээ"
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
