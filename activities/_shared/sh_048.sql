/*---
indicator_id: SH_048
name_mn: "Процесс удирдлагын хэлтэст хянагдахгүй батлагдсан журам заавар байгаа эсэх"
manual: true                    # хүн үнэлнэ (ri.py manual). SQL бичвэл бүх үйл ажиллагаанд автомат: manual-ийг хасаад доор нь SQL
status: TODO
version: 0.1.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  5-Хянагдаагүй 1-ээс дээш тохиолдол гарсан.
  3-Хянагдаагүй 1 тохиолдол гарсан
  1-Бүх журам зааврын процессыг хянасан
source_system: "JIRA, УАА"
required_info: "Нийт батлагдсан журам заавар, Процесс хянасан бүртгэл"
method: "Хянасан журам, зааврын жагсаалт/ Батлагдсан журам зааврын жагсаалт"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
