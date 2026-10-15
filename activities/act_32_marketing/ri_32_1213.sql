/*---
indicator_id: RI_32_1213
name_mn: "Банкны зах зээлд эзлэх байр суурь буурах /актив, ТТХ/"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5- Байр суурь буурсан /2уулаа/
  3- Байр суурь хэвэндээ
  1- Байр суурь өссөн /2уулаа/
source_system: "Монгол банкны мэдээлэл"
required_info: "Зах зээлд эзлэх байр суурийн мэдээ"
method: "Актив болон татан төвлөрүүлсэн хөрөнгийн хэмжээгээр зах зээлд эзлэх байр суурьд үндэслэн үнэлнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
