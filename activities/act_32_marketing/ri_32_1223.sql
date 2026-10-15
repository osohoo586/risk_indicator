/*---
indicator_id: RI_32_1223
name_mn: "Төлөвлөгөөт зар сурталчилгааны гүйцэтгэл"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-1
source_system: "МХ"
required_info: "Хийгдсэн зар сурталчигааны мэдээлэл"
method: "Хийгдсэн зар сурталчилгааны төлөвлөгөөний гүйцэтгэлд үндэслэн үнэлнэ. Бүтээгдэхүүн хөгжүүлэлтээс шалтгаалж хойшилсон зар сурталчилгааг оруулж тооцохгүй"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
