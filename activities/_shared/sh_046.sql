/*---
indicator_id: SH_046
name_mn: "Харилцагчийн сэтгэл ханамжийн индекс - ВИП сегмэнт"
manual: true                    # хүн үнэлнэ (ri.py manual). SQL бичвэл бүх үйл ажиллагаанд автомат: manual-ийг хасаад доор нь SQL
status: TODO
version: 0.1.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score4"
scale_text: |
  1-95%-100%
  2-90%-94%
  3-85%-89%
  4-80%-84%
  5-80%-с доош
source_system: "МОНХГ-СХА"
required_info: "Мэдлэгийн шалгалтын дүн Эрсдэл, Комплаенс,  Зээлийн үйл ажиллагааны журмын мэдлэг, МАБ"
method: "Сэтгэл ханамжийн судалгааны үр дүнд үндэслэн үнэлнэ"
period_text: "Хамгийн сүүлд авсан шалгалтаар"
period: latest                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
