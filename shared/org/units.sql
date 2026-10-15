-- Тайлант өдрийн байгууллагын бүтэц: SOLID (хэлтэс, алба, салбар) → BRANCHID (үйл ажиллагаа).
-- COREMIS.MAIN-ийн TDATE <= :p_report_date хамгийн сүүлийн snapshot (байхгүй бол хамгийн эртний).
-- Нэг SOLID олон BRANCHID-д орж болно. Runner (config org.shared) болон үзүүлэлтүүд ашиглана.
-- Буцаах: SOLID, BRANCHID, SOLNAME
SELECT m.SOLID                 AS SOLID,
       m.BRANCHID              AS BRANCHID,
       m.BRANCHNAME            AS SOLNAME
FROM   {{schema.main}}.MAIN m
WHERE  m.TDATE = (SELECT NVL(MAX(CASE WHEN x.TDATE <= :p_report_date THEN x.TDATE END), MIN(x.TDATE))
                  FROM   {{schema.main}}.MAIN x)
