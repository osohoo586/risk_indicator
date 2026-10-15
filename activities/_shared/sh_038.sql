/*---
indicator_id: SH_038
name_mn: "Зээл шийдвэрлэх процессын хурд"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  1-15 өдөрт
  2-16 өдөрт
  3-17 өдөрт
  4-18 өдөрт
  5-19-с дээш өдөрт. Судалгааны хурдыг хэмждэггүй.
source_system: "ЗГ-ЗМХ"
required_info: "Зээл шийдвэрлэх хугацааны мэдээ"
method: "Зээлийн үйл ажиллагаанд тусгагдсан хурдаар хэмжинэ. Зээлийн судалгааг гүйцэтгэж эхэлснээс шийдвэрлэх хүртэл хугацаагаар тооцно."
period_text: "Аудит орсноос хойш улирлын дундаж."
automatable: "Тийм"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
description: >
  Зээл шийдвэрлэх хурд: судалгаа эхэлснээс шийдвэр гарах хүртэлх хоногийн дундаж, аудит орсноос хойш
  шийдвэр гарсан хүсэлтээр. ХУУЧИН PROCEDURE-ийн жишээ: FINACLE.RA_LOAN_PKG.DECISION_SPEED нь стандарт
  баганатай SYS_REFCURSOR (:rc) буцаана — runner READ ONLY transaction дотор ажиллуулна.
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
BEGIN
  {{schema.finacle}}.RA_LOAN_PKG.DECISION_SPEED(:p_period_start, :p_report_date, :rc);
END;
