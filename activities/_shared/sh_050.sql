/*---
indicator_id: SH_050
name_mn: "ЗГ-аас улирал тутам хийж буй хяналтын үнэлгээ"
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
  1-100% ба түүнээс дээш
source_system: "ЗГ"
required_info: "ЗГ-с БПМГ-т хийсэн хяналтын үнэлгээ"
method: "Зээлийн судалгаанд хийсэн хяналтын үнэлгээний дагуу үнэлнэ."
period_text: "Аудит орсноос хойш улирлын дундаж хугацаа"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
