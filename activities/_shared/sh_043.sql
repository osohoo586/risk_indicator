/*---
indicator_id: SH_043
name_mn: "Системд хүнд алдаа гарах"
manual: true                    # хүн үнэлнэ (ri.py manual). SQL бичвэл бүх үйл ажиллагаанд автомат: manual-ийг хасаад доор нь SQL
status: TODO
version: 0.1.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  5-10-аас дээш удаа гарсан
  3-1-9 удаа гарсан
  1-алдаа гараагүй
source_system: "JIRA систем"
required_info: "Тасралт үүссэн эсэх"
method: "ЖИРА системд SDD прожектод байгаа \"хүнд алдаа\"-ны тоог гаргах"
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
