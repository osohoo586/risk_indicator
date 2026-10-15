/*---
indicator_id: RI_26_0976
name_mn: "И-Биллинг үйлчилгээний гэрээт байгууллагын өсөлт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Хамрах хугацаанд буурсан
  3-Өсөлт, бууралтгүй хэвийн
  1-Хамрах хугацаанд өссөн.
source_system: "ДБХ"
required_info: "И-Биллинг үйлчилгээний байгууллагын жагсаалт"
method: "И-Биллингийн байгууллагын тооны өөрчлөлтийг аудит орсноос хойш хугацаатай харьцуулан дүгнэнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
