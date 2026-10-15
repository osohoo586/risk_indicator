/*---
indicator_id: RI_21_0786
name_mn: "ERP хүсэлт шийдвэрлэлт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-4 хоногоос дээш хугацаанд шийдвэрлэсэн
  3-3-4 хоногт багтаан шийдвэрлэсэн
  1-3 хүртэлх хоногт багтаан шийдвэрлэсэн
source_system: "ERP, БПМГ-ПУХ"
required_info: "Дүрэм, чиг үүрэг, журам заавар"
method: "Банкинд өөрчлөгдсөн болон шинэчлэгдсэн журам зааварт дүгнэлт өгсөн хугацааг харгалзан"
period_text: "Аудит орсносс хойш хугацаанд улирлын дунджаар"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
