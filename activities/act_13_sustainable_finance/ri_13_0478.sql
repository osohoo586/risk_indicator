/*---
indicator_id: RI_13_0478
name_mn: "ESG тайлагналын тоо"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "BI"
required_info: "Төлөвлөгөөний биелэлтийн хувь"
method: |
  ОУ-ын стандартын дагуу бэлтггэсэн ESG тайлангийн тоо /өссөн/ .
  1. Ногоон зээлийн тайлан /Улирал бүр /
  2. ТоС тайлан /Хагас жил бүр/
  3. Тогтвортой хөгжлийн тайлан /Жил бүр/
  4. Хариуцлагатай банкны хэрэгжилтийн тайлан /Жил бүр/
  5. Хөрөнгийн биржийн тайлан /Жил бүр/
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
