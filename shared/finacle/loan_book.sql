-- Тайлант өдрийн зээлийн багц (FINACLE): данс бүрийн SOL, ангилал, үлдэгдэл, эрсдэлийн сан, ногоон эсэх.
-- CLASS_CODE: ХЭВИЙН / ХУГАЦАА ХЭТЭРСЭН (анхаарал хандуулах — АХЗ) / ХЭВИЙН БУС, ЭРГЭЛЗЭЭТЭЙ, МУУ (чанаргүй).
-- Ашигладаг: RI_01_0009 (АХЗ), RI_01_0010 (чанаргүй), RI_01_0011 (эрсдэлийн сан), SH_009 (ногоон зээл)
SELECT a.ACID                  AS ACID,
       a.SOL_ID                AS SOL_ID,
       a.CIF_ID                AS CIF_ID,
       c.CLASS_CODE            AS CLASS_CODE,
       c.OUTSTANDING_AMT       AS OUTSTANDING_AMT,
       c.PROVISION_AMT         AS PROVISION_AMT,
       l.IS_GREEN              AS IS_GREEN
FROM   {{schema.finacle}}.LOAN_CLASS_HIST c
JOIN   {{schema.finacle}}.GAM a ON a.ACID = c.ACID
JOIN   {{schema.finacle}}.LAM l ON l.ACID = c.ACID
WHERE  c.TXNDATE = :p_report_date
  AND  a.SCHM_TYPE = 'LAA'
