"""Стандарт банкны DEMO өгөгдөл: COREMIS, FINACLE, ERP, CARDZONE, JIRA (+ ClickHouse cardzone_dwh).

    python tests/local/seed_bank.py      # Docker Oracle + ClickHouse-д үүсгэж ачаална (setup.sh дуудна)
    python tests/local/demo_check.py     # runner → ClickHouse ↔ эталон (bank_golden.py) тулгана

Нэг генератор: Oracle seed, ClickHouse DWH, эталон тооцоо (bank_golden.py) бүгд build()-ийн НЭГ датаг ашиглана.
random.Random(SEED) — давтан ажиллуулахад яг ижил дата.

Бүтэц (банкны стандарт нэршил; багана нь ТААМАГ — бодит нэр өөр бол зөвхөн shared/org, shared/erp,
shared/finacle-ийн SQL-ийг засна):
  COREMIS   MAIN (SOLID → BRANCHID бүтэц, TDATE snapshot), GL_REPORT_DATA (BI тайлан GL3003a / IN2003),
            GL_USER_BRANCH, CUSTOMER_COMPLAINT (ХҮГ / ДАГ), GREEN_LOAN_PLAN, CUSTOMER_PLAN,
            CUSTOMER_ACTIVITY_MONTHLY, LOAN_MONITORING_QA, DOC_ARCHIVE_CHECK, LOAN_COMMITTEE_CHECK
  FINACLE   SOL, CMG (харилцагч), GAM (данс), LAM (зээл), LOAN_CLASS_HIST (ангилал, эрсдэлийн сан),
            LOAN_APPLICATION (судалгаа → шийдвэр), RA_LOAN_PKG (хуучин procedure: SYS_REFCURSOR)
  ERP       HR_ORG_DEPARTMENT (хэлтэс → SOLID), ERP_HR_POSITION, ERP_EMPLOYEE, ERP_EMPLOYEE_KEY,
            EMPLOYEE_HISTORY (томилгоо), ERP_HR_CURRENT_STATUS, HRM_EMP_FAMILY_PEOPLE,
            ERP_HR_APPRAISAL, ERP_HR_TRAINING, ERP_HR_STAFF_PLAN, ERP_HR_DISCIPLINE
  CARDZONE  CARD, TERMINAL, CARD_TXN        (ClickHouse cardzone_dwh.card_txn = CARD_TXN-ийн хуулбар)
  JIRA      ABH_JIRA_NEW, JIRAISSUE_NEW

Бүтцийн өөрчлөлт (MAIN snapshot-оор автоматаар тусна):
  2026-01-01 snapshot: SOL 819 (ББГ-Төслийн санхүүжилтийн хэлтэс) 998-д, 818 ба 898 байхгүй
                       (2025-12-31 болон түүнээс өмнөх тайлант өдөрт ч энэ snapshot — хамгийн эртнийх)
  2026-03-01 snapshot: 819 хаагдаж 818 үүссэн (ажилтнууд TRANSFER — гарсанд тооцогдохгүй; зээл, харилцагч
                       818 рүү), ХНУГ-т 898 хэлтэс (2026-02-01 нээгдсэн) 1006-д
  2026-09-15 snapshot: config/activity_units.csv-тэй ижил
"""
import csv
import datetime as dt
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = Path(__file__).resolve().parent / "demo"
SEED = 20261014
D = dt.date
DAY = dt.timedelta(days=1)
DATA_END = D(2026, 9, 30)            # source-д ачаалагдсан сүүлийн өдөр
HIST_START = D(2023, 1, 1)           # ажилтны симуляцийн эхлэл (өмнөх ажилтнууд анхны байдлаар)
SNAPSHOTS = (D(2026, 1, 1), D(2026, 3, 1), D(2026, 9, 15))   # 03-01: бүтцийн өөрчлөлт
REPORT_DATES = (D(2026, 6, 30), D(2026, 9, 30))
REORG_DATE = D(2026, 3, 1)           # 819 → 818
HR_NEW_DATE = D(2026, 2, 1)          # 898 шинэ хэлтэс

# local demo-д ТОДРУУЛАХ 5 бүлэгт түр BRANCHID (config/activity_map.csv-д хоосон хэвээр), 2001-д түр SOL
DEMO_UNITS = [   # (нэр, SOLID, BRANCHID)
    ("ЖДБГ-Жижиг дунд бизнесийн хэлтэс (DEMO)", 701, 9002),
    ("ЖДБГ-ЖДБ-ийн зээлийн алба (DEMO)", 702, 9002),
    ("ХОСБГ-Гадаад эх үүсвэрийн алба (DEMO)", 710, 9010),
    ("ТЭҮГ-Гадны эх үүсвэрийн санхүүжилтийн алба (DEMO)", 711, 9011),
    ("АТМ-ын гүйлгээний алба", 933, 9020),          # 1169 (Касс)-д ч мөн орно — нэг SOL 2 BRANCHID
    ("ДШГ-Дижитал шилжилтийн алба (DEMO)", 721, 9021),
    ("ГТТГ-Гадаад төлбөр тооцооны хэлтэс (DEMO)", 731, 2001),   # 2001-д config/activity_units.csv-д SOL алга
]
RETAIL_BRANCHID = 1500                    # салбарын сүлжээ — ямар ч үйл ажиллагаанд ороогүй (банк нийтэд л орно)
RETAIL = ["Сансар", "Баянзүрх", "Хан-Уул", "Сүхбаатар", "Чингэлтэй", "Баянгол", "Дархан", "Эрдэнэт", "Дорнод",
          "Өмнөговь", "Ховд", "Говь-Алтай"]
OLD_SOL = (819, "ББГ-Төслийн санхүүжилтийн хэлтэс", 998)
NEW_SOL = 818
HR_BRANCHID = 1006
HR_NEW_SOL = 898
MANAGER_TITLES = {"Захирал", "Салбарын захирал", "Ахлах мэргэжилтэн", "Кассын эрхлэгч"}
CORP_BRANCHID = 998
LOAN_CLASSES = ("ХЭВИЙН", "ХУГАЦАА ХЭТЭРСЭН", "ХЭВИЙН БУС", "ЭРГЭЛЗЭЭТЭЙ", "МУУ")
NPL_CLASSES = ("ХЭВИЙН БУС", "ЭРГЭЛЗЭЭТЭЙ", "МУУ")
PROVISION_RATE = {"ХЭВИЙН": 0.01, "ХУГАЦАА ХЭТЭРСЭН": 0.05, "ХЭВИЙН БУС": 0.25, "ЭРГЭЛЗЭЭТЭЙ": 0.5, "МУУ": 1.0}
# Мастерийн ангиллын текст (RI_01_0020, RI_01_0021) — өгөгдөлд яг ингэж бичигдэнэ
DOC_VIOLATIONS = {5: "Гарын үсэггүй баримтаар гүйлгээ хийсэн эсвэл гүйлгээний баримтгүй, хяналтгүй",
                  4: "Гарын үсэг зөрүүтэй баримтаар гүйлгээ хийсэн", 3: "Гүйлгээ буруу хийсэн.",
                  2: "Шимтгэл аваагүй, буруу авсан", 1: "Зөрчилгүй"}
LC_VIOLATIONS = {5: "Цохолттой олгосон материалын бүрдэл хугацаа хэтэрсэн.",
                 4: "ЗХБ-н материалын бүрдэл дутуу /Гэрчилгээ, гэрээ/", 3: "Эрх зүйн бичиг баримт алдаатай",
                 2: "Програмд мэдээлэл бүртгээгүй /барьцаа, ХЗ/", 1: "Зөрчилгүй"}
GL_PKEYS = {   # BI тайлангийн мөр (PKEY) → үзүүлэлт (activities/act_01_*/ri_01_*.sql params.p_pkeys)
    "GL3003a": {10001: "Зээл (₮)", 10002: "Зээл (валют)", 20001: "Харилцах", 20002: "Хадгаламж",
                30001: "Лизингийн багц", 25430: "Салбар хоорондын тооцоо (хасагдана)",
                25487: "Дотоод шилжүүлэг (хасагдана)"},
    "IN2003": {40001: "Цэвэр хүүгийн орлого", 40002: "Шимтгэлийн цэвэр орлого", 42200: "Алтны арилжааны ашиг",
               43001: "Лизингийн хүүгийн орлого", 44001: "КҮБ-ийн шимтгэлийн орлого"},
}

# ── Бүтэц: {SCHEMA: {TABLE: (баганууд, constraint, тайлбар)}} ────────────────────
SCHEMAS = {
    "COREMIS": {
        "MAIN": ([("TDATE", "DATE NOT NULL"), ("SOLID", "NUMBER(6) NOT NULL"), ("BRANCHID", "NUMBER(6) NOT NULL"),
                  ("SUBBRANCHID", "NUMBER(6)"), ("BRANCHNAME", "VARCHAR2(200) NOT NULL")],
                 ["CONSTRAINT MAIN_PK PRIMARY KEY (TDATE, SOLID, BRANCHID)"],
                 "Байгууллагын бүтэц: SOLID (хэлтэс, алба, салбар) → BRANCHID (үйл ажиллагаа). TDATE = snapshot "
                 "огноо; тайлант өдрийн бүтэц = TDATE <= тайлант өдөр хамгийн сүүлийнх. Нэг SOL олон BRANCHID-д орж болно"),
        "GL_USER_BRANCH": ([("SUB_BRANCH", "NUMBER(6) NOT NULL"), ("USER_BRANCH", "NUMBER(6) NOT NULL")],
                           ["CONSTRAINT GL_USER_BRANCH_PK PRIMARY KEY (SUB_BRANCH)"],
                           "BI тайлангийн хэрэглэгчийн салбар (GL3003a-д бүртгэлтэй SOL л тооцогдоно)"),
        "GL_REPORT_DATA": ([("TXNDATE", "DATE NOT NULL"), ("REPORTNO", "VARCHAR2(20) NOT NULL"),
                            ("VERSION", "VARCHAR2(5) NOT NULL"), ("BRANCH", "NUMBER(6) NOT NULL"),
                            ("PKEY", "NUMBER(10) NOT NULL"), ("PKEY_NAME", "VARCHAR2(200)"),
                            ("BUDGET", "NUMBER(20,2)"), ("RUNNING_BUDGET", "NUMBER(20,2)"), ("BALANCE", "NUMBER(20,2)")],
                           ["CONSTRAINT GL_REPORT_DATA_PK PRIMARY KEY (TXNDATE, REPORTNO, VERSION, BRANCH, PKEY)"],
                           "BI тайлан: GL3003a (балансын төлөвлөгөө: BUDGET ↔ BALANCE), IN2003 (орлого: RUNNING_BUDGET "
                           "↔ BALANCE). VERSION 1 = батлагдсан, 2 = ноорог (тооцохгүй)"),
        "CUSTOMER_COMPLAINT": ([("COMPLAINT_ID", "NUMBER(10) NOT NULL"), ("SOLID", "NUMBER(6) NOT NULL"),
                                ("REG_DATE", "DATE NOT NULL"), ("CHANNEL", "VARCHAR2(20) NOT NULL"),
                                ("IS_BANK_FAULT", "CHAR(1) NOT NULL"), ("STATUS", "VARCHAR2(30) NOT NULL"),
                                ("DESCRIPTION", "VARCHAR2(400)")],
                               ["CONSTRAINT CUSTOMER_COMPLAINT_PK PRIMARY KEY (COMPLAINT_ID)",
                                "CONSTRAINT CUSTOMER_COMPLAINT_CH_CK CHECK (CHANNEL IN ('ХҮГ', 'ДАГ', 'ЦАХИМ'))",
                                "CONSTRAINT CUSTOMER_COMPLAINT_F_CK CHECK (IS_BANK_FAULT IN ('Y', 'N'))"],
                               "Гомдол: ХҮГ (харилцагчийн үйлчилгээ), ДАГ (дотоод аудит), ЦАХИМ. IS_BANK_FAULT = банк, "
                               "ажилтны буруугаас"),
        "GREEN_LOAN_PLAN": ([("TXNDATE", "DATE NOT NULL"), ("SOLID", "NUMBER(6) NOT NULL"),
                             ("PLAN_AMT", "NUMBER(20,2) NOT NULL")],
                            ["CONSTRAINT GREEN_LOAN_PLAN_PK PRIMARY KEY (TXNDATE, SOLID)"],
                            "Ногоон зээлийн үлдэгдлийн төлөвлөгөө (тайлант өдрөөр)"),
        "CUSTOMER_PLAN": ([("TXNDATE", "DATE NOT NULL"), ("SOLID", "NUMBER(6) NOT NULL"),
                           ("SEGMENT", "VARCHAR2(10) NOT NULL"), ("ACTIVE_PLAN", "NUMBER(10)"),
                           ("DIGITAL_ACTIVE_PLAN", "NUMBER(10)")],
                          ["CONSTRAINT CUSTOMER_PLAN_PK PRIMARY KEY (TXNDATE, SOLID, SEGMENT)"],
                          "Идэвхтэй / дижитал идэвхтэй харилцагчийн тооны төлөвлөгөө (primary SOL-оор)"),
        "CUSTOMER_ACTIVITY_MONTHLY": ([("MONTH_END", "DATE NOT NULL"), ("CIF_ID", "VARCHAR2(20) NOT NULL"),
                                       ("TXN_COUNT", "NUMBER(6) NOT NULL"), ("LOGIN_COUNT", "NUMBER(6) NOT NULL"),
                                       ("HAS_LOAN", "CHAR(1) NOT NULL"), ("HAS_TD", "CHAR(1) NOT NULL"),
                                       ("HAS_CREDIT_CARD", "CHAR(1) NOT NULL"), ("HAS_LC_GUARANTEE", "CHAR(1) NOT NULL")],
                                      ["CONSTRAINT CUST_ACT_MONTHLY_PK PRIMARY KEY (MONTH_END, CIF_ID)"],
                                      "Харилцагчийн сарын идэвх: гүйлгээ, цахим нэвтрэлт, бүтээгдэхүүн (сарын сүүлээр)"),
        "LOAN_MONITORING_QA": ([("REVIEW_ID", "NUMBER(10) NOT NULL"), ("SOLID", "NUMBER(6) NOT NULL"),
                                ("QUARTER_END", "DATE NOT NULL"), ("SCORE_PCT", "NUMBER(5,1) NOT NULL")],
                               ["CONSTRAINT LOAN_MONITORING_QA_PK PRIMARY KEY (REVIEW_ID)"],
                               "Зээлийн эргэн хяналтын чанарын улирлын үнэлгээ (ЗГ-ЗМХ), %"),
        "DOC_ARCHIVE_CHECK": ([("CHECK_ID", "NUMBER(10) NOT NULL"), ("SOLID", "NUMBER(6) NOT NULL"),
                               ("CHECK_DATE", "DATE NOT NULL"), ("VIOLATION_LEVEL", "NUMBER(1) NOT NULL"),
                               ("VIOLATION_TEXT", "VARCHAR2(400) NOT NULL")],
                              ["CONSTRAINT DOC_ARCHIVE_CHECK_PK PRIMARY KEY (CHECK_ID)"],
                              "Бүртгэлийн баримтын (архивын) шалгалт: VIOLATION_LEVEL 1 = зөрчилгүй … 5 = ноцтой"),
        "LOAN_COMMITTEE_CHECK": ([("CHECK_ID", "NUMBER(10) NOT NULL"), ("SOLID", "NUMBER(6) NOT NULL"),
                                  ("CHECK_DATE", "DATE NOT NULL"), ("VIOLATION_LEVEL", "NUMBER(1) NOT NULL"),
                                  ("VIOLATION_TEXT", "VARCHAR2(400) NOT NULL")],
                                 ["CONSTRAINT LOAN_COMMITTEE_CHECK_PK PRIMARY KEY (CHECK_ID)"],
                                 "Зээлийн хорооны (ЗХБ) материалын шалгалт: VIOLATION_LEVEL 1 = зөрчилгүй … 5"),
    },
    "FINACLE": {
        "SOL": ([("SOL_ID", "NUMBER(6) NOT NULL"), ("SOL_DESC", "VARCHAR2(200) NOT NULL"), ("OPEN_DATE", "DATE"),
                 ("CLOSE_DATE", "DATE")],
                ["CONSTRAINT SOL_PK PRIMARY KEY (SOL_ID)"], "Үйлчилгээний нэгж (Service Outlet)"),
        "CMG": ([("CIF_ID", "VARCHAR2(20) NOT NULL"), ("CUST_NAME", "VARCHAR2(200) NOT NULL"),
                 ("SEGMENT", "VARCHAR2(10) NOT NULL"), ("PRIMARY_SOL_ID", "NUMBER(6) NOT NULL"), ("REG_DATE", "DATE")],
                ["CONSTRAINT CMG_PK PRIMARY KEY (CIF_ID)",
                 "CONSTRAINT CMG_SOL_FK FOREIGN KEY (PRIMARY_SOL_ID) REFERENCES FINACLE.SOL (SOL_ID)",
                 "CONSTRAINT CMG_SEGMENT_CK CHECK (SEGMENT IN ('CORP', 'SME', 'RETAIL'))"],
                "Харилцагч (Customer Master General). PRIMARY_SOL_ID = харилцагчийг хариуцсан нэгж"),
        "GAM": ([("ACID", "VARCHAR2(20) NOT NULL"), ("FORACID", "VARCHAR2(20) NOT NULL"),
                 ("CIF_ID", "VARCHAR2(20) NOT NULL"), ("SOL_ID", "NUMBER(6) NOT NULL"),
                 ("SCHM_TYPE", "VARCHAR2(5) NOT NULL"), ("ACCT_OPN_DATE", "DATE NOT NULL"), ("ACCT_CLS_DATE", "DATE"),
                 ("ACCT_CRNCY_CODE", "VARCHAR2(3) NOT NULL")],
                ["CONSTRAINT GAM_PK PRIMARY KEY (ACID)", "CONSTRAINT GAM_FORACID_UK UNIQUE (FORACID)",
                 "CONSTRAINT GAM_CMG_FK FOREIGN KEY (CIF_ID) REFERENCES FINACLE.CMG (CIF_ID)",
                 "CONSTRAINT GAM_SOL_FK FOREIGN KEY (SOL_ID) REFERENCES FINACLE.SOL (SOL_ID)",
                 "CONSTRAINT GAM_SCHM_CK CHECK (SCHM_TYPE IN ('LAA', 'SBA', 'CAA', 'TDA'))"],
                "Данс (General Account Master): LAA зээл, SBA хадгаламж, CAA харилцах, TDA хугацаатай"),
        "LAM": ([("ACID", "VARCHAR2(20) NOT NULL"), ("SANCT_AMT", "NUMBER(20,2) NOT NULL"),
                 ("SANCT_DATE", "DATE NOT NULL"), ("MATURITY_DATE", "DATE"), ("INT_RATE", "NUMBER(6,3)"),
                 ("IS_GREEN", "CHAR(1) NOT NULL")],
                ["CONSTRAINT LAM_PK PRIMARY KEY (ACID)",
                 "CONSTRAINT LAM_GAM_FK FOREIGN KEY (ACID) REFERENCES FINACLE.GAM (ACID)"],
                "Зээлийн данс (Loan Account Master). IS_GREEN = ногоон зээл"),
        "LOAN_CLASS_HIST": ([("TXNDATE", "DATE NOT NULL"), ("ACID", "VARCHAR2(20) NOT NULL"),
                             ("CLASS_CODE", "VARCHAR2(30) NOT NULL"), ("OUTSTANDING_AMT", "NUMBER(20,2) NOT NULL"),
                             ("PROVISION_AMT", "NUMBER(20,2) NOT NULL"), ("DPD", "NUMBER(5) NOT NULL")],
                            ["CONSTRAINT LOAN_CLASS_HIST_PK PRIMARY KEY (TXNDATE, ACID)",
                             "CONSTRAINT LOAN_CLASS_HIST_GAM_FK FOREIGN KEY (ACID) REFERENCES FINACLE.GAM (ACID)",
                             "CONSTRAINT LOAN_CLASS_HIST_CK CHECK (CLASS_CODE IN ('ХЭВИЙН', 'ХУГАЦАА ХЭТЭРСЭН', "
                             "'ХЭВИЙН БУС', 'ЭРГЭЛЗЭЭТЭЙ', 'МУУ'))"],
                            "Зээлийн ангилал (сарын сүүлээр): ХУГАЦАА ХЭТЭРСЭН = анхаарал хандуулах (АХЗ), "
                            "ХЭВИЙН БУС + ЭРГЭЛЗЭЭТЭЙ + МУУ = чанаргүй; PROVISION_AMT = эрсдэлийн сан"),
        "LOAN_APPLICATION": ([("APP_ID", "NUMBER(10) NOT NULL"), ("CIF_ID", "VARCHAR2(20) NOT NULL"),
                              ("SOL_ID", "NUMBER(6) NOT NULL"), ("STUDY_START_DATE", "DATE NOT NULL"),
                              ("DECISION_DATE", "DATE"), ("DECISION", "VARCHAR2(10)"), ("AMOUNT", "NUMBER(20,2)")],
                             ["CONSTRAINT LOAN_APPLICATION_PK PRIMARY KEY (APP_ID)",
                              "CONSTRAINT LOAN_APP_SOL_FK FOREIGN KEY (SOL_ID) REFERENCES FINACLE.SOL (SOL_ID)",
                              "CONSTRAINT LOAN_APP_DEC_CK CHECK (DECISION IN ('APPROVED', 'REJECTED'))"],
                             "Зээлийн хүсэлт: судалгаа эхэлсэн → шийдвэр (DECISION NULL = шийдэгдээгүй)"),
    },
    "ERP": {
        "HR_ORG_DEPARTMENT": ([("DEPARTMENT_ID", "NUMBER(10) NOT NULL"), ("DEPARTMENT_NAME", "VARCHAR2(200) NOT NULL"),
                               ("SOLID", "NUMBER(6) NOT NULL"), ("PARENT_DEPARTMENT_ID", "NUMBER(10)"),
                               ("OPEN_DATE", "DATE NOT NULL"), ("CLOSE_DATE", "DATE")],
                              ["CONSTRAINT HR_ORG_DEPARTMENT_PK PRIMARY KEY (DEPARTMENT_ID)"],
                              "Байгууллагын нэгж (хэлтэс, алба, салбар). SOLID = Finacle/COREMIS-ийн SOL — ERP ↔ "
                              "эрсдэлийн үнэлгээний холбоос"),
        "ERP_HR_POSITION": ([("POSITION_ID", "NUMBER(10) NOT NULL"), ("DEPARTMENT_ID", "NUMBER(10) NOT NULL"),
                             ("POSITION_NAME", "VARCHAR2(200) NOT NULL"), ("IS_MANAGER", "CHAR(1) NOT NULL"),
                             ("POSITION_GRADE", "NUMBER(2)")],
                            ["CONSTRAINT ERP_HR_POSITION_PK PRIMARY KEY (POSITION_ID)",
                             "CONSTRAINT ERP_HR_POSITION_DEP_FK FOREIGN KEY (DEPARTMENT_ID) "
                             "REFERENCES ERP.HR_ORG_DEPARTMENT (DEPARTMENT_ID)",
                             "CONSTRAINT ERP_HR_POSITION_MGR_CK CHECK (IS_MANAGER IN ('Y', 'N'))"],
                            "Албан тушаал. IS_MANAGER = Y: удирдах (захирал, ахлах, кассын эрхлэгч)"),
        "ERP_EMPLOYEE": ([("EMPLOYEE_ID", "NUMBER(10) NOT NULL"), ("LAST_NAME", "VARCHAR2(100) NOT NULL"),
                          ("FIRST_NAME", "VARCHAR2(100) NOT NULL"), ("REGISTER_NO", "VARCHAR2(10) NOT NULL"),
                          ("GENDER", "CHAR(1) NOT NULL"), ("BIRTH_DATE", "DATE NOT NULL"),
                          ("HIRE_DATE", "DATE NOT NULL"), ("END_DATE", "DATE"), ("END_REASON", "VARCHAR2(100)")],
                         ["CONSTRAINT ERP_EMPLOYEE_PK PRIMARY KEY (EMPLOYEE_ID)",
                          "CONSTRAINT ERP_EMPLOYEE_REG_UK UNIQUE (REGISTER_NO)",
                          "CONSTRAINT ERP_EMPLOYEE_DATES_CK CHECK (END_DATE IS NULL OR END_DATE >= HIRE_DATE)"],
                         "Ажилтан. HIRE_DATE = банкинд орсон, END_DATE = ажлаас гарсан (ажилласан сүүлийн) өдөр"),
        "ERP_EMPLOYEE_KEY": ([("EMPLOYEE_ID", "NUMBER(10) NOT NULL"), ("EMP_CODE", "VARCHAR2(20) NOT NULL"),
                              ("FINACLE_USER_ID", "VARCHAR2(20)"), ("AD_LOGIN", "VARCHAR2(50)")],
                             ["CONSTRAINT ERP_EMPLOYEE_KEY_PK PRIMARY KEY (EMPLOYEE_ID)",
                              "CONSTRAINT ERP_EMPLOYEE_KEY_UK UNIQUE (EMP_CODE)",
                              "CONSTRAINT ERP_EMPLOYEE_KEY_FK FOREIGN KEY (EMPLOYEE_ID) "
                              "REFERENCES ERP.ERP_EMPLOYEE (EMPLOYEE_ID)"],
                             "Системүүдийн түлхүүр: ажилтны код, Finacle хэрэглэгч, AD нэвтрэх нэр"),
        "EMPLOYEE_HISTORY": ([("HISTORY_ID", "NUMBER(10) NOT NULL"), ("EMPLOYEE_ID", "NUMBER(10) NOT NULL"),
                              ("DEPARTMENT_ID", "NUMBER(10) NOT NULL"), ("POSITION_ID", "NUMBER(10) NOT NULL"),
                              ("ACTION_TYPE", "VARCHAR2(20) NOT NULL"), ("START_DATE", "DATE NOT NULL"),
                              ("END_DATE", "DATE")],
                             ["CONSTRAINT EMPLOYEE_HISTORY_PK PRIMARY KEY (HISTORY_ID)",
                              "CONSTRAINT EMPLOYEE_HISTORY_EMP_FK FOREIGN KEY (EMPLOYEE_ID) "
                              "REFERENCES ERP.ERP_EMPLOYEE (EMPLOYEE_ID)",
                              "CONSTRAINT EMPLOYEE_HISTORY_DEP_FK FOREIGN KEY (DEPARTMENT_ID) "
                              "REFERENCES ERP.HR_ORG_DEPARTMENT (DEPARTMENT_ID)",
                              "CONSTRAINT EMPLOYEE_HISTORY_POS_FK FOREIGN KEY (POSITION_ID) "
                              "REFERENCES ERP.ERP_HR_POSITION (POSITION_ID)",
                              "CONSTRAINT EMPLOYEE_HISTORY_ACT_CK CHECK (ACTION_TYPE IN ('HIRE', 'PROMOTION', "
                              "'TRANSFER'))",
                              "CONSTRAINT EMPLOYEE_HISTORY_DATES_CK CHECK (END_DATE IS NULL OR END_DATE >= START_DATE)"],
                             "Томилгооны түүх: START_DATE … END_DATE (хоёулаа орно, NULL = одоо). Нэг өдөр нэг л мөр. "
                             "TRANSFER, PROMOTION нь гаралт биш"),
        "ERP_HR_CURRENT_STATUS": ([("EMPLOYEE_ID", "NUMBER(10) NOT NULL"), ("STATUS_CODE", "VARCHAR2(20) NOT NULL"),
                                   ("DEPARTMENT_ID", "NUMBER(10)"), ("POSITION_ID", "NUMBER(10)"),
                                   ("STATUS_DATE", "DATE NOT NULL")],
                                  ["CONSTRAINT ERP_HR_CURRENT_STATUS_PK PRIMARY KEY (EMPLOYEE_ID)",
                                   "CONSTRAINT ERP_HR_CURRENT_STATUS_CK CHECK (STATUS_CODE IN ('ACTIVE', 'LEAVE', "
                                   "'MATERNITY', 'TERMINATED'))"],
                                  "ӨНӨӨДРИЙН төлөв (snapshot). Түүхэн тайлант өдөрт ашиглахгүй — EMPLOYEE_HISTORY"),
        "HRM_EMP_FAMILY_PEOPLE": ([("FAMILY_ID", "NUMBER(10) NOT NULL"), ("EMPLOYEE_ID", "NUMBER(10) NOT NULL"),
                                   ("RELATION", "VARCHAR2(30) NOT NULL"), ("FULL_NAME", "VARCHAR2(200) NOT NULL"),
                                   ("BIRTH_DATE", "DATE"), ("WORKS_IN_BANK", "CHAR(1) NOT NULL")],
                                  ["CONSTRAINT HRM_EMP_FAMILY_PEOPLE_PK PRIMARY KEY (FAMILY_ID)",
                                   "CONSTRAINT HRM_EMP_FAMILY_EMP_FK FOREIGN KEY (EMPLOYEE_ID) "
                                   "REFERENCES ERP.ERP_EMPLOYEE (EMPLOYEE_ID)"],
                                  "Ажилтны гэр бүлийн гишүүд (хамаарал бүхий этгээд)"),
        "ERP_HR_APPRAISAL": ([("APPRAISAL_ID", "NUMBER(10) NOT NULL"), ("EMPLOYEE_ID", "NUMBER(10) NOT NULL"),
                              ("PERIOD_END", "DATE NOT NULL"), ("SCORE_PCT", "NUMBER(5,1) NOT NULL")],
                             ["CONSTRAINT ERP_HR_APPRAISAL_PK PRIMARY KEY (APPRAISAL_ID)",
                              "CONSTRAINT ERP_HR_APPRAISAL_UK UNIQUE (EMPLOYEE_ID, PERIOD_END)",
                              "CONSTRAINT ERP_HR_APPRAISAL_EMP_FK FOREIGN KEY (EMPLOYEE_ID) "
                              "REFERENCES ERP.ERP_EMPLOYEE (EMPLOYEE_ID)"],
                             "Ажлын гүйцэтгэлийн улирлын үнэлгээ (%), PERIOD_END = улирлын сүүл"),
        "ERP_HR_TRAINING": ([("TRAINING_ID", "NUMBER(10) NOT NULL"), ("EMPLOYEE_ID", "NUMBER(10) NOT NULL"),
                             ("TRAINING_NAME", "VARCHAR2(200) NOT NULL"), ("TRAINING_TYPE", "VARCHAR2(20) NOT NULL"),
                             ("START_DATE", "DATE NOT NULL"), ("HOURS", "NUMBER(5,1) NOT NULL"),
                             ("IS_PAID", "CHAR(1) NOT NULL")],
                            ["CONSTRAINT ERP_HR_TRAINING_PK PRIMARY KEY (TRAINING_ID)",
                             "CONSTRAINT ERP_HR_TRAINING_EMP_FK FOREIGN KEY (EMPLOYEE_ID) "
                             "REFERENCES ERP.ERP_EMPLOYEE (EMPLOYEE_ID)"],
                            "Сургалт (дотоод / гадаад), HOURS = суусан цаг"),
        "ERP_HR_STAFF_PLAN": ([("PLAN_ID", "NUMBER(10) NOT NULL"), ("DEPARTMENT_ID", "NUMBER(10) NOT NULL"),
                               ("POSITION_ID", "NUMBER(10) NOT NULL"), ("APPROVED_COUNT", "NUMBER(4) NOT NULL"),
                               ("EFFECTIVE_FROM", "DATE NOT NULL"), ("EFFECTIVE_TO", "DATE")],
                              ["CONSTRAINT ERP_HR_STAFF_PLAN_PK PRIMARY KEY (PLAN_ID)",
                               "CONSTRAINT ERP_HR_STAFF_PLAN_DEP_FK FOREIGN KEY (DEPARTMENT_ID) "
                               "REFERENCES ERP.HR_ORG_DEPARTMENT (DEPARTMENT_ID)"],
                              "Батлагдсан орон тоо (албан тушаал бүрээр), EFFECTIVE_FROM … EFFECTIVE_TO (NULL = одоо)"),
        "ERP_HR_KNOWLEDGE_TEST": ([("TEST_ID", "NUMBER(10) NOT NULL"), ("EMPLOYEE_ID", "NUMBER(10) NOT NULL"),
                                   ("TEST_DATE", "DATE NOT NULL"), ("SCORE_PCT", "NUMBER(5,1) NOT NULL")],
                                  ["CONSTRAINT ERP_HR_KNOWLEDGE_TEST_PK PRIMARY KEY (TEST_ID)",
                                   "CONSTRAINT ERP_HR_KNOWLEDGE_TEST_EMP_FK FOREIGN KEY (EMPLOYEE_ID) "
                                   "REFERENCES ERP.ERP_EMPLOYEE (EMPLOYEE_ID)"],
                                  "Мэргэжлийн мэдлэгийн шалгалт (%), хагас жил тутам"),
        "ERP_HR_DISCIPLINE": ([("CASE_ID", "NUMBER(10) NOT NULL"), ("EMPLOYEE_ID", "NUMBER(10) NOT NULL"),
                               ("ACTION_DATE", "DATE NOT NULL"), ("CASE_TYPE", "VARCHAR2(20) NOT NULL"),
                               ("PENALTY", "VARCHAR2(100) NOT NULL"), ("DESCRIPTION", "VARCHAR2(400)")],
                              ["CONSTRAINT ERP_HR_DISCIPLINE_PK PRIMARY KEY (CASE_ID)",
                               "CONSTRAINT ERP_HR_DISCIPLINE_EMP_FK FOREIGN KEY (EMPLOYEE_ID) "
                               "REFERENCES ERP.ERP_EMPLOYEE (EMPLOYEE_ID)",
                               "CONSTRAINT ERP_HR_DISCIPLINE_CK CHECK (CASE_TYPE IN ('ЁС ЗҮЙ', 'САХИЛГА'))"],
                              "Сахилгын шийтгэл. CASE_TYPE = ЁС ЗҮЙ: ёс зүйн зөрчлөөр"),
    },
    "CARDZONE": {
        "TERMINAL": ([("TERMINAL_ID", "VARCHAR2(10) NOT NULL"), ("SOL_ID", "NUMBER(6) NOT NULL"),
                      ("TERMINAL_TYPE", "VARCHAR2(5) NOT NULL"), ("MERCHANT_NAME", "VARCHAR2(200)")],
                     ["CONSTRAINT TERMINAL_PK PRIMARY KEY (TERMINAL_ID)",
                      "CONSTRAINT TERMINAL_TYPE_CK CHECK (TERMINAL_TYPE IN ('ATM', 'POS'))"],
                     "Терминал (ATM, POS) — хариуцсан SOL"),
        "CARD": ([("CARD_ID", "VARCHAR2(20) NOT NULL"), ("CIF_ID", "VARCHAR2(20) NOT NULL"),
                  ("ISSUE_SOL_ID", "NUMBER(6) NOT NULL"), ("PRODUCT", "VARCHAR2(30) NOT NULL"),
                  ("ISSUE_DATE", "DATE NOT NULL"), ("STATUS", "VARCHAR2(10) NOT NULL")],
                 ["CONSTRAINT CARD_PK PRIMARY KEY (CARD_ID)"], "Карт: гаргасан SOL, бүтээгдэхүүн"),
        "CARD_TXN": ([("TXN_ID", "NUMBER(12) NOT NULL"), ("CARD_ID", "VARCHAR2(20) NOT NULL"),
                      ("TERMINAL_ID", "VARCHAR2(10) NOT NULL"), ("TXN_DATE", "DATE NOT NULL"),
                      ("AMOUNT", "NUMBER(18,2) NOT NULL"), ("CHANNEL", "VARCHAR2(5) NOT NULL"),
                      ("IS_FRAUD", "CHAR(1) NOT NULL")],
                     ["CONSTRAINT CARD_TXN_PK PRIMARY KEY (TXN_ID)",
                      "CONSTRAINT CARD_TXN_CARD_FK FOREIGN KEY (CARD_ID) REFERENCES CARDZONE.CARD (CARD_ID)"],
                     "Картын гүйлгээ. IS_FRAUD = залилан гэж баталгаажсан"),
    },
    "JIRA": {
        "ABH_JIRA_NEW": ([("ID", "NUMBER(10) NOT NULL"), ("DOHIOLOL_COMP", "VARCHAR2(100)"),
                          ("SALBAR_NEGJ_NER", "VARCHAR2(200)")],
                         ["CONSTRAINT ABH_JIRA_NEW_PK PRIMARY KEY (ID)"], "АБХ: дохиоллын түгшүүрийн бүртгэл"),
        "JIRAISSUE_NEW": ([("ID", "NUMBER(10) NOT NULL"), ("ISSUENUM", "NUMBER(10) NOT NULL"),
                           ("ISSUETYPE", "VARCHAR2(10) NOT NULL"), ("CREATED", "DATE NOT NULL")],
                          ["CONSTRAINT JIRAISSUE_NEW_PK PRIMARY KEY (ID)"], "Jira issue"),
        "ACTION_PLAN": ([("ITEM_ID", "NUMBER(10) NOT NULL"), ("BRANCHID", "NUMBER(6) NOT NULL"),
                         ("TITLE", "VARCHAR2(200) NOT NULL"), ("CREATED", "DATE NOT NULL"), ("DUE_DATE", "DATE NOT NULL"),
                         ("RESOLVED_DATE", "DATE")],
                        ["CONSTRAINT ACTION_PLAN_PK PRIMARY KEY (ITEM_ID)"],
                        "Үйл ажиллагааны action plan-ы ажил (Jira): хугацаа, шийдвэрлэсэн өдөр"),
    },
    "GRC": {
        "AUDIT_ENGAGEMENT": ([("ENGAGEMENT_ID", "NUMBER(10) NOT NULL"), ("BRANCHID", "NUMBER(6) NOT NULL"),
                              ("START_DATE", "DATE NOT NULL"), ("END_DATE", "DATE NOT NULL"),
                              ("RATING_CODE", "NUMBER(1) NOT NULL")],
                             ["CONSTRAINT AUDIT_ENGAGEMENT_PK PRIMARY KEY (ENGAGEMENT_ID)",
                              "CONSTRAINT AUDIT_ENGAGEMENT_CK CHECK (RATING_CODE IN (1, 3, 5))"],
                             "Дотоод аудит: END_DATE = тайлан гарсан өдөр («аудит орсон»). RATING_CODE 1 Хангалттай, "
                             "3 Сайжруулах шаардлагатай, 5 Хангалтгүй"),
        "AUDIT_FINDING": ([("FINDING_ID", "NUMBER(10) NOT NULL"), ("ENGAGEMENT_ID", "NUMBER(10) NOT NULL"),
                           ("RISK_LEVEL", "VARCHAR2(10) NOT NULL"), ("DUE_DATE", "DATE NOT NULL"),
                           ("STATUS", "VARCHAR2(20) NOT NULL"), ("CLOSED_DATE", "DATE")],
                          ["CONSTRAINT AUDIT_FINDING_PK PRIMARY KEY (FINDING_ID)",
                           "CONSTRAINT AUDIT_FINDING_ENG_FK FOREIGN KEY (ENGAGEMENT_ID) "
                           "REFERENCES GRC.AUDIT_ENGAGEMENT (ENGAGEMENT_ID)",
                           "CONSTRAINT AUDIT_FINDING_RISK_CK CHECK (RISK_LEVEL IN ('ӨНДӨР', 'ДУНД', 'БАГА'))",
                           "CONSTRAINT AUDIT_FINDING_ST_CK CHECK (STATUS IN ('НЭЭЛТТЭЙ', 'ХЭРЭГЖСЭН'))"],
                          "Аудитын асуудал (зөвлөмж): эрсдэлийн түвшин, хэрэгжүүлэх хугацаа, хэрэгжсэн өдөр"),
        "REMOTE_AUDIT_CHECK": ([("CHECK_ID", "NUMBER(10) NOT NULL"), ("BRANCHID", "NUMBER(6) NOT NULL"),
                                ("CHECK_DATE", "DATE NOT NULL"), ("RESULT_CODE", "NUMBER(1) NOT NULL")],
                               ["CONSTRAINT REMOTE_AUDIT_CHECK_PK PRIMARY KEY (CHECK_ID)"],
                               "Зайны аудит: RESULT_CODE 1 зөрчилгүй … 5 илтгэх хуудас бичигдсэн"),
        "EXTERNAL_REVIEW": ([("REVIEW_ID", "NUMBER(10) NOT NULL"), ("BRANCHID", "NUMBER(6) NOT NULL"),
                             ("REVIEWER", "VARCHAR2(30) NOT NULL"), ("REVIEW_DATE", "DATE NOT NULL"),
                             ("RESULT_CODE", "NUMBER(1) NOT NULL")],
                            ["CONSTRAINT EXTERNAL_REVIEW_PK PRIMARY KEY (REVIEW_ID)",
                             "CONSTRAINT EXTERNAL_REVIEW_CK CHECK (REVIEWER IN ('МБ', 'ХӨНДЛӨНГИЙН АУДИТ'))"],
                            "Монгол банкны шалгалт (1 Сайн … 5 Муу), хөндлөнгийн аудитын зөвлөмж (1 бага, 3 дунд, 5 өндөр)"),
        "POLICY_DOCUMENT": ([("DOC_ID", "NUMBER(10) NOT NULL"), ("BRANCHID", "NUMBER(6) NOT NULL"),
                             ("DOC_NAME", "VARCHAR2(200) NOT NULL"), ("APPROVED_DATE", "DATE NOT NULL"),
                             ("LAST_REVISION_DATE", "DATE NOT NULL")],
                            ["CONSTRAINT POLICY_DOCUMENT_PK PRIMARY KEY (DOC_ID)"],
                            "Үйл ажиллагааны дүрэм, журам, заавар — сүүлд шинэчилсэн өдөр"),
        "INFOSEC_INCIDENT": ([("INCIDENT_ID", "NUMBER(10) NOT NULL"), ("SOLID", "NUMBER(6) NOT NULL"),
                              ("INCIDENT_DATE", "DATE NOT NULL"), ("DATA_TYPE", "VARCHAR2(20) NOT NULL"),
                              ("SEVERITY", "NUMBER(1) NOT NULL")],
                             ["CONSTRAINT INFOSEC_INCIDENT_PK PRIMARY KEY (INCIDENT_ID)",
                              "CONSTRAINT INFOSEC_INCIDENT_CK CHECK (DATA_TYPE IN ('БАНК', 'ХАРИЛЦАГЧ'))"],
                             "Мэдээллийн нууц задруулсан тохиолдол (DLP): SEVERITY 4 гадагш гаргасан, 5 давтагдсан"),
    },
}

# FINACLE-ийн хуучин procedure (RI_01_0013 нь :rc-ээр уншина) — seed_bank.py үүсгэнэ
FINACLE_PACKAGE = """
CREATE OR REPLACE PACKAGE FINACLE.RA_LOAN_PKG AS
  -- Зээл шийдвэрлэх хугацаа: SOL бүрийн шийдвэр гарсан хүсэлтийн тоо, нийт хоног (стандарт багана)
  PROCEDURE DECISION_SPEED(p_from IN DATE, p_to IN DATE, p_rc OUT SYS_REFCURSOR);
END RA_LOAN_PKG;
/
CREATE OR REPLACE PACKAGE BODY FINACLE.RA_LOAN_PKG AS
  PROCEDURE DECISION_SPEED(p_from IN DATE, p_to IN DATE, p_rc OUT SYS_REFCURSOR) IS
  BEGIN
    OPEN p_rc FOR
      SELECT 'SOL' AS ENTITY_LEVEL, TO_CHAR(a.SOL_ID) AS ENTITY_ID,
             SUM(a.DECISION_DATE - a.STUDY_START_DATE) AS NUMERATOR, COUNT(*) AS DENOMINATOR,
             SUM(a.DECISION_DATE - a.STUDY_START_DATE) / COUNT(*) AS VALUE, COUNT(*) AS SOURCE_ROW_COUNT
      FROM   FINACLE.LOAN_APPLICATION a
      WHERE  a.DECISION IS NOT NULL
        AND  a.DECISION_DATE >= p_from AND a.DECISION_DATE < p_to + 1
      GROUP  BY a.SOL_ID;
  END DECISION_SPEED;
END RA_LOAN_PKG;
"""

CH_CARD_TXN = """CREATE TABLE IF NOT EXISTS {db}.card_txn
(
    txn_id UInt64, card_id String, issue_sol_id UInt32, terminal_id String, txn_date Date,
    amount Decimal(18, 2), channel LowCardinality(String), is_fraud UInt8
)
ENGINE = MergeTree ORDER BY (txn_date, issue_sol_id, txn_id)
COMMENT 'CARDZONE.CARD_TXN-ийн DWH хуулбар (картыг гаргасан SOL-той)'"""


# ── Бүтэц, SOL ────────────────────────────────────────────────────────────────
def config_units() -> list[tuple]:
    """config/activity_units.csv (2026-09-15 snapshot): (нэр, SOLID, BRANCHID, SUBBRANCHID)."""
    with (ROOT / "config" / "activity_units.csv").open(encoding="utf-8-sig", newline="") as f:
        return [(r["BRANCHNAME"].strip(), int(r["SOLID"]), int(r["BRANCHID"]),
                 int(r["SUBBRANCHID"]) if (r.get("SUBBRANCHID") or "").strip() else None)
                for r in csv.DictReader(f) if (r.get("SOLID") or "").strip()]


def main_rows() -> list[tuple]:
    """COREMIS.MAIN: (TDATE, SOLID, BRANCHID, SUBBRANCHID, BRANCHNAME)."""
    current = [(n, s, b, sb) for n, s, b, sb in config_units()]
    current += [(n, s, b, None) for n, s, b in DEMO_UNITS]
    current += [(f"{name} салбар", 101 + i, RETAIL_BRANCHID, None) for i, name in enumerate(RETAIL)]
    old = [u for u in current if not (u[1] == NEW_SOL and u[2] == CORP_BRANCHID)
           and not (u[1] == HR_NEW_SOL and u[2] == HR_BRANCHID)]
    old.append((OLD_SOL[1], OLD_SOL[0], OLD_SOL[2], None))
    out = [(SNAPSHOTS[0], s, b, sb, n) for n, s, b, sb in old]
    out += [(snap, s, b, sb, n) for snap in SNAPSHOTS[1:] for n, s, b, sb in current]
    return sorted(out, key=lambda r: (r[0], r[2], r[1]))


def sol_names(main: list[tuple]) -> dict[int, str]:
    out: dict[int, str] = {}
    for _, s, _, _, n in sorted(main, key=lambda r: r[0], reverse=True):
        out.setdefault(s, n)
    return out


def units_at(main: list[tuple], d: dt.date) -> list[tuple]:
    """Тайлант өдрийн бүтэц (TDATE <= d хамгийн сүүлийн snapshot, байхгүй бол хамгийн эртний)."""
    dates = sorted({r[0] for r in main})
    past = [x for x in dates if x <= d]
    snap = past[-1] if past else dates[0]
    return [r for r in main if r[0] == snap]


def sols_of_branch(main: list[tuple], branch_id: int, d: dt.date) -> set[int]:
    return {r[1] for r in units_at(main, d) if r[2] == int(branch_id)}


def dept_id(sol: int) -> int:
    return 50000 + sol


# ── Хүний нөөцийн симуляци ───────────────────────────────────────────────────
@dataclass
class Inc:
    """Нэг томилгоо (EMPLOYEE_HISTORY-ийн мөр)."""
    sol: int
    title: str
    start: dt.date
    end: dt.date | None
    action: str = "HIRE"
    prev: "Inc | None" = None
    nxt: "Inc | None" = None
    emp_id: int = 0


@dataclass
class Profile:
    kind: str
    titles: list
    mean_stay: float                 # жил — эргэцийг тодорхойлно
    gap: float                       # сул орон тооны дундаж хоног
    init_years: float                # 2023 оны эхний ажилтнуудын тухайн албан тушаалд ажилласан дээд хугацаа
    appraisal: float                 # гүйцэтгэлийн дундаж %
    training: float                  # жилд нэг ажилтанд ногдох сургалтын цаг
    complaints: float                # улиралд ногдох гомдол
    dag: float                       # улиралд ДАГ-т гомдол ирэх магадлал
    ethics: float                    # жилд ёс зүйн зөрчил
    extra_plan: int = 0              # батлагдсан боловч хэзээ ч бөглөгдөөгүй орон тоо
    expand_q3: int = 0               # 2026-07-01-ээс нэмэгдсэн орон тоо
    open_date: dt.date = D(2010, 1, 1)
    close_date: dt.date | None = None


def _days(years: float) -> dt.timedelta:
    return dt.timedelta(days=max(1, int(years * 365.25)))


def _chain(rng: random.Random, prof: Profile, first: dt.date) -> list[tuple]:
    """first өдрөөс эхлэн гаднаас ажилд авсан ажилтнуудын (start, end) дараалал DATA_END хүртэл."""
    out, t = [], first
    while t <= DATA_END:
        end = t + dt.timedelta(days=max(45, int(rng.expovariate(1 / prof.mean_stay) * 365.25)))
        if end > DATA_END:
            out.append((t, None))
            break
        out.append((t, end))
        t = end + dt.timedelta(days=1 + int(rng.expovariate(1 / prof.gap)))
    return out


def profiles(rng: random.Random, sols: dict[int, str], hr_sols: set[int]) -> dict[int, Profile]:
    out = {}
    for sol in sorted(sols):
        if 101 <= sol < 101 + len(RETAIL):
            kind, size = "retail", rng.randint(8, 12)
            titles = ["Салбарын захирал", "Кассын эрхлэгч"] + ["Теллер"] * (size // 2) \
                + ["Харилцагчийн мэргэжилтэн"] * (size - 2 - size // 2)
        elif sol in hr_sols:
            kind, size = "hr", {862: 6, 896: 5, 897: 5, 898: 3}.get(sol, 4)
            titles = ["Захирал"] + ["Хүний нөөцийн менежер"] * (size - 1)
        else:
            kind, size = "hq", rng.choice([3, 4, 4, 5, 5, 6, 7, 8])
            titles = ["Захирал"] + (["Ахлах мэргэжилтэн"] if size >= 5 else []) \
                + ["Мэргэжилтэн"] * (size - 1 - (size >= 5))
        p = Profile(kind, titles,
                    mean_stay=rng.choice([2.2, 3, 4, 5, 6.5, 8, 11]),
                    gap=rng.choice([15, 30, 60, 120]),
                    init_years=rng.choice([1.5, 3, 4.5, 6, 9]),
                    appraisal=rng.uniform(83, 101),
                    training=rng.uniform(7, 21),
                    complaints=rng.uniform(1, 4.5) if kind == "retail" else rng.choice([0, 0, 0, 0.3, 0.7, 1.5, 3]),
                    dag=rng.choice([0, 0, 0, 0, 0.05, 0.15]),
                    ethics=rng.choice([0, 0, 0, 0, 0.3, 0.8]),
                    extra_plan=1 if rng.random() < 0.15 else 0,
                    expand_q3=1 if rng.random() < 0.15 else 0)
        if sol == NEW_SOL:
            p.open_date = REORG_DATE
        if sol == OLD_SOL[0]:
            p.close_date = REORG_DATE - DAY
        if sol == HR_NEW_SOL:
            p.open_date = HR_NEW_DATE
        out[sol] = p
    out[NEW_SOL].titles = list(out[OLD_SOL[0]].titles)        # 819-ийн ажилтнууд 818 рүү
    return out


def simulate_hr(rng: random.Random, profs: dict[int, Profile]) -> list[Inc]:
    """Хэлтэс бүрийн орон тоо (slot) → томилгоонуудын гинж (дэвшүүлэлт, шилжилт, бүтцийн өөрчлөлттэй)."""
    heads: list[Inc] = []
    for sol, p in sorted(profs.items()):
        if sol == NEW_SOL:
            continue                                    # 819-ийн гинж 818-д үргэлжилнэ (доор)
        spec: list[list[Inc]] = []
        mgr_slots = []
        n_slots = len(p.titles) + (p.expand_q3 if sol != OLD_SOL[0] else 0)
        for k in range(n_slots):
            title = p.titles[k] if k < len(p.titles) else _base_title(p)
            if k >= len(p.titles):                      # 2026-07-01-ээс нэмэгдсэн орон тоо
                timeline = _chain(rng, p, D(2026, 7, 1) + dt.timedelta(days=int(rng.expovariate(1 / p.gap))))
            elif p.open_date > HIST_START:              # шинэ хэлтэс
                timeline = _chain(rng, p, p.open_date + dt.timedelta(days=int(rng.uniform(0, 40))))
            else:
                pos_start = HIST_START - dt.timedelta(days=int(rng.uniform(30, p.init_years * 365.25)))
                first_end = HIST_START + dt.timedelta(days=int(rng.expovariate(1 / p.mean_stay) * 365.25))
                if first_end > DATA_END:
                    timeline = [(pos_start, None)]
                else:
                    timeline = [(pos_start, first_end)] + _chain(
                        rng, p, first_end + dt.timedelta(days=1 + int(rng.expovariate(1 / p.gap))))
            incs = [Inc(sol, title, s, e) for s, e in timeline]
            (mgr_slots if title in MANAGER_TITLES else spec).append(incs)

        # Удирдах албан тушаал: шинэ хүн 50% дотоодоос (тухайн хэлтсийн мэргэжилтэн дэвшинэ)
        promoted, pre_heads = set(), []
        events = sorted(((inc.start, i, j) for i, slot in enumerate(mgr_slots) for j, inc in enumerate(slot)),
                        key=lambda x: (x[0], x[1], x[2]))
        for t, i, j in events:
            inc = mgr_slots[i][j]
            if j == 0 and inc.start < HIST_START:       # анхны удирдлага: өмнө нь мэргэжилтэн байсан
                hire = inc.start - dt.timedelta(days=int(rng.uniform(0, 6) * 365.25))
                if hire < inc.start - dt.timedelta(days=60):
                    pre = Inc(sol, _base_title(p), hire, inc.start - DAY)
                    pre.nxt, inc.prev, inc.action = inc, pre, "PROMOTION"
                    pre_heads.append(pre)
                continue
            if rng.random() >= 0.5:
                continue
            cands = [(si, sj) for si, slot in enumerate(spec) for sj, s in enumerate(slot)
                     if s.start <= t - dt.timedelta(days=60) and (s.end is None or s.end >= t)
                     and s.nxt is None and id(s) not in promoted]
            if not cands:
                continue
            si, sj = cands[int(rng.random() * len(cands))]
            s = spec[si][sj]
            s.end = t - DAY
            s.nxt, inc.prev, inc.action = inc, s, "PROMOTION"
            promoted.add(id(s))
            # Мэргэжилтний орон тоо сул болж, дараа нь шинэ хүн
            spec[si] = spec[si][:sj + 1] + [Inc(sol, s.title, a, b) for a, b in
                                             _chain(rng, p, t + dt.timedelta(days=1 + int(rng.expovariate(1 / p.gap))))]
        for slot in spec + mgr_slots:
            heads += [inc for inc in slot if inc.prev is None]
        heads += pre_heads                              # анхны удирдлагын өмнөх (мэргэжилтэн) томилгоо
    _reorg(heads)
    _swaps(rng, heads)
    return heads


def _base_title(p: Profile) -> str:
    return next((t for t in p.titles if t not in MANAGER_TITLES), p.titles[-1])


def _walk(head: Inc):
    x = head
    while x is not None:
        yield x
        x = x.nxt


def _reorg(heads: list[Inc]) -> None:
    """819 → 818 (REORG_DATE): тухайн өдөр ажиллаж байсан томилгоо 819-д дуусаж, 818-д TRANSFER."""
    for h in heads:
        for inc in list(_walk(h)):
            if inc.sol != OLD_SOL[0]:
                continue
            if inc.start >= REORG_DATE:
                inc.sol = NEW_SOL
            elif inc.end is None or inc.end >= REORG_DATE:
                new = Inc(NEW_SOL, inc.title, REORG_DATE, inc.end, "TRANSFER", prev=inc, nxt=inc.nxt)
                if inc.nxt is not None:
                    inc.nxt.prev = new
                inc.end, inc.nxt = REORG_DATE - DAY, new


def _swaps(rng: random.Random, heads: list[Inc], n: int = 6) -> None:
    """Хэлтэс хооронд мэргэжилтэн солилцох (A ↔ B) — хэлтсийн орон тоо хэвээр, гаралт биш."""
    t_opts = [D(2025, 11, 1), D(2026, 4, 1), D(2026, 8, 1)]
    for k in range(n):
        t = t_opts[k % len(t_opts)]
        cands = [inc for h in heads for inc in _walk(h)
                 if inc.title == "Мэргэжилтэн" and inc.nxt is None and inc.start <= t - dt.timedelta(days=60)
                 and (inc.end is None or inc.end >= t + dt.timedelta(days=30))
                 and inc.sol not in (OLD_SOL[0], NEW_SOL)]
        if len(cands) < 2:
            return
        a = cands[int(rng.random() * len(cands))]
        others = [c for c in cands if c.sol != a.sol]
        if not others:
            continue
        b = others[int(rng.random() * len(others))]
        a2 = Inc(b.sol, b.title, t, b.end, "TRANSFER", prev=a)
        b2 = Inc(a.sol, a.title, t, a.end, "TRANSFER", prev=b)
        a.end, a.nxt = t - DAY, a2
        b.end, b.nxt = t - DAY, b2


# ── build ─────────────────────────────────────────────────────────────────────
LAST = ["Бат", "Дорж", "Болд", "Ганбаатар", "Сүхбаатар", "Түмэн", "Энх", "Отгон", "Нямдорж", "Цэрэн", "Мөнх",
        "Лхагва", "Ганзориг", "Батсүх", "Даваа", "Пүрэв", "Наран", "Жаргал", "Оюун", "Эрдэнэ"]
FIRST_M = ["Бат-Эрдэнэ", "Тэмүүлэн", "Ганболд", "Өсөхбаяр", "Билгүүн", "Тэмүүжин",
           "Анхбаяр", "Мөнх-Оргил", "Энхтүвшин", "Цогбаяр"]
FIRST_F = ["Сарнай", "Номин", "Анужин", "Мишээл", "Хулан", "Оюунчимэг", "Энхжин", "Солонго", "Уянга", "Нандин"]
REG_LETTERS = "АБВГДЕЖЗИЙКЛМНОӨПРСТУҮФХЦЧШЭЮЯ"


def _q_ends(a: dt.date, b: dt.date) -> list[dt.date]:
    out, y, q = [], a.year, (a.month - 1) // 3 + 1
    while True:
        m = 3 * q
        e = (D(y, m, 31) if m in (3, 12) else D(y, m, 30))
        if e > b:
            return out
        if e >= a:
            out.append(e)
        y, q = (y + 1, 1) if q == 4 else (y, q + 1)


def _month_ends(a: dt.date, b: dt.date) -> list[dt.date]:
    out, y, m = [], a.year, a.month
    while True:
        e = (D(y + (m == 12), m % 12 + 1, 1) - DAY)
        if e > b:
            return out
        if e >= a:
            out.append(e)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def _active(inc: Inc, x: dt.date) -> bool:
    return inc.start <= x and (inc.end is None or inc.end >= x)


def build() -> dict:
    """{"SCHEMA.TABLE": [мөр, ...]} + "_meta" (эталонд хэрэгтэй дотоод бүтэц)."""
    rng = random.Random(SEED)
    main = main_rows()
    names = sol_names(main)
    sols = dict(sorted(names.items()))
    hr_sols = {r[1] for r in main if r[2] == HR_BRANCHID}
    profs = profiles(rng, sols, hr_sols)
    data: dict[str, list] = defaultdict(list)
    data["COREMIS.MAIN"] = main

    # ── ERP: хэлтэс, албан тушаал ──
    pos_of: dict[tuple, int] = {}
    for sol, p in profs.items():
        data["ERP.HR_ORG_DEPARTMENT"].append((dept_id(sol), sols[sol], sol, None, p.open_date, p.close_date))
        for k, title in enumerate(dict.fromkeys(p.titles)):
            pid = dept_id(sol) * 10 + k
            pos_of[(sol, title)] = pid
            grade = 9 if title in ("Захирал", "Салбарын захирал") else 7 if title in MANAGER_TITLES else 5
            data["ERP.ERP_HR_POSITION"].append((pid, dept_id(sol), title, "Y" if title in MANAGER_TITLES else "N", grade))
    plan_id = 0
    for sol, p in sorted(profs.items()):
        counts = defaultdict(int)
        for t in p.titles:
            counts[t] += 1
        base = _base_title(p)
        versions = [(max(p.open_date, D(2025, 1, 1)), D(2026, 6, 30), 0), (D(2026, 7, 1), None, p.expand_q3)]
        if p.close_date:
            versions = [(D(2025, 1, 1), p.close_date, 0)]
        for frm, to, extra in versions:
            if to is not None and to < frm:
                continue
            for title, cnt in counts.items():
                plan_id += 1
                add = (p.extra_plan + extra) if title == base else 0
                data["ERP.ERP_HR_STAFF_PLAN"].append((plan_id, dept_id(sol), pos_of[(sol, title)], cnt + add, frm, to))

    # ── ERP: ажилтнууд ──
    heads = simulate_hr(rng, profs)
    heads.sort(key=lambda h: (h.start, h.sol, h.title))
    incs: list[Inc] = []
    hid = 0
    used_reg = set()
    for n, h in enumerate(heads, start=1):
        chain = list(_walk(h))
        for inc in chain:
            inc.emp_id = n
            hid += 1
            data["ERP.EMPLOYEE_HISTORY"].append((hid, n, dept_id(inc.sol), pos_of[(inc.sol, inc.title)],
                                                 "HIRE" if inc is h else inc.action, inc.start, inc.end))
            incs.append(inc)
        last = chain[-1]
        g = "M" if rng.random() < 0.45 else "F"
        while True:
            reg = rng.choice(REG_LETTERS) + rng.choice(REG_LETTERS) + f"{rng.randint(0, 99999999):08d}"
            if reg not in used_reg:
                used_reg.add(reg)
                break
        birth = h.start - dt.timedelta(days=int(rng.uniform(22, 45) * 365.25))
        reason = rng.choice(["Өөрийн хүсэлтээр", "Өөрийн хүсэлтээр", "Гэрээ дууссан", "Тэтгэвэр", "Халагдсан"]) \
            if last.end else None
        data["ERP.ERP_EMPLOYEE"].append((n, rng.choice(LAST), rng.choice(FIRST_M if g == "M" else FIRST_F), reg, g,
                                         birth, h.start, last.end, reason))
        data["ERP.ERP_EMPLOYEE_KEY"].append((n, f"GB{n:05d}", f"U{100000 + n}", f"emp{n:05d}"))
        if last.end:
            status = ("TERMINATED", None, None, last.end)
        else:
            r = rng.random()
            code = "MATERNITY" if r < 0.02 else "LEAVE" if r < 0.04 else "ACTIVE"
            status = (code, dept_id(last.sol), pos_of[(last.sol, last.title)], DATA_END)
        data["ERP.ERP_HR_CURRENT_STATUS"].append((n, *status))
        for _ in range(rng.choice([0, 1, 1, 2, 2, 3])):
            data["ERP.HRM_EMP_FAMILY_PEOPLE"].append((
                len(data["ERP.HRM_EMP_FAMILY_PEOPLE"]) + 1, n, rng.choice(["Эхнэр", "Нөхөр", "Хүү", "Охин", "Эцэг", "Эх"]),
                f"{rng.choice(LAST)} {rng.choice(FIRST_M + FIRST_F)}",
                birth + dt.timedelta(days=int(rng.uniform(-30, 30) * 365.25)), "Y" if rng.random() < 0.05 else "N"))

    # Гүйцэтгэлийн үнэлгээ (улирал бүр, тухайн өдөр ажиллаж байсан, 60+ хоног ажилласан; 3% үнэлгээгүй)
    app_id = 0
    for qe in _q_ends(D(2024, 1, 1), D(2026, 6, 30)):
        for inc in incs:
            if _active(inc, qe) and inc.start <= qe - dt.timedelta(days=60) and rng.random() > 0.03:
                app_id += 1
                score = round(min(110.0, max(60.0, rng.gauss(profs[inc.sol].appraisal, 4))), 1)
                data["ERP.ERP_HR_APPRAISAL"].append((app_id, inc.emp_id, qe, score))
    # Сургалт (2024-01-01 … DATA_END, ажиллаж байх хугацаандаа)
    tr_id = 0
    courses = ["Мөнгө угаахтай тэмцэх", "Мэдээллийн аюулгүй байдал", "Харилцагчийн үйлчилгээ", "Зээлийн шинжилгээ",
               "Удирдах ур чадвар", "Эрсдэлийн удирдлага", "Excel / BI", "Ёс зүйн дүрэм"]
    for me in _month_ends(D(2024, 1, 1), DATA_END):
        ms = me.replace(day=1)
        for inc in incs:
            if not (inc.start <= me and (inc.end is None or inc.end >= ms)):
                continue
            p = profs[inc.sol]
            if rng.random() < p.training / 6 / 12:
                lo = max(ms, inc.start)
                hi = min(me, inc.end) if inc.end else me
                day = lo + dt.timedelta(days=int(rng.uniform(0, (hi - lo).days + 1)))
                tr_id += 1
                hours = rng.choice([2, 4, 4, 6, 8, 8, 16])
                kind = "ГАДААД" if rng.random() < 0.2 else "ДОТООД"
                data["ERP.ERP_HR_TRAINING"].append((tr_id, inc.emp_id, rng.choice(courses), kind, day, float(hours),
                                                    "Y" if kind == "ГАДААД" else "N"))
    # Сахилга, ёс зүй
    case_id = 0
    for sol, p in sorted(profs.items()):
        for year in (2024, 2025, 2026):
            for case_type, lam in (("ЁС ЗҮЙ", p.ethics), ("САХИЛГА", 0.6)):
                for _ in range(_poisson(rng, lam)):
                    day = D(year, 1, 1) + dt.timedelta(days=int(rng.uniform(0, 365)))
                    if day > DATA_END:
                        continue
                    act = [inc for inc in incs if inc.sol == sol and _active(inc, day)]
                    if not act:
                        continue
                    case_id += 1
                    data["ERP.ERP_HR_DISCIPLINE"].append((
                        case_id, act[int(rng.random() * len(act))].emp_id, day, case_type,
                        rng.choice(["Сануулах", "Цалин бууруулах", "Ажлаас халах"]),
                        "Ашиг сонирхлын зөрчил" if case_type == "ЁС ЗҮЙ" else "Ажлын цаг зөрчсөн"))

    # ── FINACLE / COREMIS ──
    for sol in sols:
        p = profs[sol]
        data["FINACLE.SOL"].append((sol, sols[sol], p.open_date, p.close_date))
    data["COREMIS.GL_USER_BRANCH"] = [(sol, sol) for sol in sols if sol != 816]   # 816 бүртгэлгүй (хасагдана)
    _gl(rng, data, sols)
    _complaints(rng, data, sols, profs)
    _customers_loans(rng, data, main)
    _checks(rng, data, main)
    _cards(rng, data, sols)
    _jira(rng, data, sols)
    _knowledge(rng, data, incs, profs)
    _grc(random.Random(SEED + 2), data, sols)
    data["_meta"] = {"incs": incs, "profiles": profs, "sols": sols}
    return dict(data)


def _poisson(rng: random.Random, lam: float) -> int:
    if lam <= 0:
        return 0
    k, p, l = 0, 1.0, math.exp(-lam)
    while True:
        p *= rng.random()
        if p <= l:
            return k
        k += 1


def _gl(rng, data, sols):
    for d in REPORT_DATES:
        for sol in sols:
            if sol == OLD_SOL[0]:
                continue
            for reportno, pkeys in GL_PKEYS.items():
                for pkey in pkeys:
                    base = rng.uniform(2e9, 40e9) * (300 if pkey in (25430, 25487) else 1)
                    ful = rng.uniform(0.84, 1.06)
                    if reportno == "GL3003a":
                        data["COREMIS.GL_REPORT_DATA"].append((d, reportno, "1", sol, pkey, pkeys[pkey],
                                                               round(base, 2), None, round(base * ful, 2)))
                    else:
                        run = base * (d.month / 12)
                        for ver, f in (("1", ful), ("2", ful * rng.uniform(0.6, 1.4))):    # 2 = ноорог
                            data["COREMIS.GL_REPORT_DATA"].append((d, reportno, ver, sol, pkey, pkeys[pkey],
                                                                   round(base, 2), round(run, 2), round(run * f, 2)))


def _complaints(rng, data, sols, profs):
    cid = 0
    for qe in _q_ends(D(2024, 1, 1), D(2026, 12, 31)):
        qs = D(qe.year, qe.month - 2, 1)
        for sol in sols:
            p = profs[sol]
            n = _poisson(rng, p.complaints)
            dag = rng.random() < p.dag
            for k in range(n + int(dag)):
                day = qs + dt.timedelta(days=int(rng.uniform(0, (qe - qs).days + 1)))
                if day > DATA_END or day < p.open_date or (p.close_date and day > p.close_date):
                    continue
                cid += 1
                is_dag = k == n
                channel = "ДАГ" if is_dag else ("ЦАХИМ" if rng.random() < 0.2 else "ХҮГ")
                status = "ШИЙДВЭРЛЭСЭН" if rng.random() < 0.85 else "ХҮЛЭЭГДЭЖ БУЙ"
                data["COREMIS.CUSTOMER_COMPLAINT"].append((
                    cid, sol, day, channel, "Y" if rng.random() < 0.65 else "N", status,
                    rng.choice(["Гүйлгээ удаан", "Шимтгэл буруу", "Ажилтны харилцаа", "Мэдээлэл буруу өгсөн"])))


def _customers_loans(rng, data, main):
    """Харилцагч, данс, зээл (ангилал, эрсдэлийн сан), хүсэлт, идэвх, төлөвлөгөө."""
    now = units_at(main, DATA_END)
    corp = sorted(sols_of_branch(main, CORP_BRANCHID, DATA_END))           # 808 … 818
    groups = [("CORP", s, 22) for s in corp] + [("SME", s, 18) for s in (701, 702)] \
        + [("CORP", 815, 14)] + [("RETAIL", 101 + i, 12) for i in range(len(RETAIL))] \
        + [("CORP", s, 6) for s in sorted({r[1] for r in now if r[2] in (1167, 1168, 1166)})]
    risk = {s: rng.choice([(0.02, 0.01), (0.04, 0.02), (0.05, 0.035), (0.07, 0.05), (0.03, 0.06)])
            for _, s, _ in groups}
    green_share = {s: rng.uniform(0.05, 0.3) for _, s, _ in groups}
    cif_n = acid_n = 0
    loans = []
    for seg, sol, n in groups:
        for _ in range(n):
            cif_n += 1
            cif = f"C{cif_n:07d}"
            reg = D(2015, 1, 1) + dt.timedelta(days=int(rng.uniform(0, 3800)))
            data["FINACLE.CMG"].append((cif, f"{seg} харилцагч {cif_n}", seg, sol, reg))
            for schm in ("CAA", "TDA", "LAA", "LAA"):
                if schm == "TDA" and rng.random() < 0.5 or schm == "LAA" and rng.random() < 0.35:
                    continue
                acid_n += 1
                acid = f"A{acid_n:08d}"
                opn = max(reg, D(2019, 1, 1)) + dt.timedelta(days=int(rng.uniform(0, 2000)))
                if opn > D(2026, 6, 1):
                    opn = D(2026, 6, 1) - dt.timedelta(days=int(rng.uniform(0, 300)))
                data["FINACLE.GAM"].append((acid, f"{sol:04d}{acid_n:08d}", cif, sol, schm, opn, None, "MNT"))
                if schm == "LAA":
                    amt = rng.uniform(5e7, 3e9) * (8 if seg == "CORP" else 1)
                    green = "Y" if rng.random() < green_share[sol] else "N"
                    data["FINACLE.LAM"].append((acid, round(amt, 2), opn, opn + dt.timedelta(days=365 * 3),
                                                round(rng.uniform(12, 22), 3), green))
                    loans.append((acid, sol, amt, cif))
    for d in REPORT_DATES:
        for acid, sol, amt, _ in loans:
            att, npl = risk[sol]
            r = rng.random()
            cls = ("ХУГАЦАА ХЭТЭРСЭН" if r < att else rng.choice(NPL_CLASSES) if r < att + npl else "ХЭВИЙН")
            out = round(amt * rng.uniform(0.3, 0.95), 2)
            prov = round(out * PROVISION_RATE[cls] * rng.uniform(0.6, 1.25), 2)
            dpd = 0 if cls == "ХЭВИЙН" else rng.randint(31, 89) if cls == "ХУГАЦАА ХЭТЭРСЭН" else rng.randint(90, 400)
            data["FINACLE.LOAN_CLASS_HIST"].append((d, acid, cls, out, prov, dpd))
    # Ногоон зээлийн төлөвлөгөө: 1 (998), 2 (9002), 6 (2000) үйл ажиллагааны SOL
    green_sols = sorted(set(corp) | {701, 702, 815})
    for d in REPORT_DATES:
        green = defaultdict(float)
        lam = {r[0]: r[5] for r in data["FINACLE.LAM"]}
        sol_of = {r[0]: r[3] for r in data["FINACLE.GAM"]}
        for r in data["FINACLE.LOAN_CLASS_HIST"]:
            if r[0] == d and lam.get(r[1]) == "Y":
                green[sol_of[r[1]]] += r[3]
        for s in green_sols:
            if s in sols_of_branch(main, CORP_BRANCHID, d) or s in (701, 702, 815):
                data["COREMIS.GREEN_LOAN_PLAN"].append((d, s, round(max(green[s], 1e8) * rng.uniform(0.88, 1.12), 2)))
    # Зээлийн хүсэлт (судалгаа → шийдвэр)
    app = 0
    speed = {s: rng.choice([11, 14, 15.5, 16.5, 17.5, 19, 22]) for _, s, _ in groups}
    cifs = defaultdict(list)
    for cif, _, seg, sol, _ in data["FINACLE.CMG"]:
        cifs[sol].append(cif)
    for sol in sorted(cifs):
        for _ in range(int(rng.uniform(8, 20))):
            start = D(2024, 3, 1) + dt.timedelta(days=int(rng.uniform(0, (DATA_END - D(2024, 3, 1)).days)))
            dur = max(3, int(rng.gauss(speed.get(sol, 16), 3)))
            dec = start + dt.timedelta(days=dur)
            app += 1
            if dec > DATA_END:
                data["FINACLE.LOAN_APPLICATION"].append((app, rng.choice(cifs[sol]), sol, start, None, None,
                                                         round(rng.uniform(5e7, 2e9), 2)))
            else:
                data["FINACLE.LOAN_APPLICATION"].append((app, rng.choice(cifs[sol]), sol, start, dec,
                                                         "APPROVED" if rng.random() < 0.8 else "REJECTED",
                                                         round(rng.uniform(5e7, 2e9), 2)))
    # Харилцагчийн сарын идэвх (CORP, 998-ийн SOL) + төлөвлөгөө
    has_loan = {r[3] for r in loans}
    has_td = {r[2] for r in data["FINACLE.GAM"] if r[4] == "TDA"}
    corp_cifs = [(cif, sol) for cif, _, seg, sol, _ in data["FINACLE.CMG"] if seg == "CORP" and sol in corp]
    prop = {cif: rng.choice([0.2, 0.5, 0.8, 0.95]) for cif, _ in corp_cifs}
    card = {cif: "Y" if rng.random() < 0.2 else "N" for cif, _ in corp_cifs}
    lcg = {cif: "Y" if rng.random() < 0.1 else "N" for cif, _ in corp_cifs}
    for me in _month_ends(D(2026, 4, 1), DATA_END):
        for cif, _ in corp_cifs:
            busy = rng.random() < prop[cif]
            data["COREMIS.CUSTOMER_ACTIVITY_MONTHLY"].append((
                me, cif, rng.randint(3, 40) if busy else rng.randint(0, 2), rng.randint(2, 20) if rng.random() < prop[cif]
                else rng.randint(0, 1), "Y" if cif in has_loan else "N", "Y" if cif in has_td else "N", card[cif], lcg[cif]))
    for d in REPORT_DATES:
        for s in sorted(sols_of_branch(main, CORP_BRANCHID, d)):
            n = sum(1 for _, sol in corp_cifs if sol == s)
            if not n:
                continue
            digital = round(n * rng.uniform(0.45, 0.8)) if s in (811, 812, 814) else None
            data["COREMIS.CUSTOMER_PLAN"].append((d, s, "CORP", round(n * rng.uniform(0.8, 1.1)), digital))


def _checks(rng, data, main):
    """Эргэн хяналтын чанар (улирал), бүртгэлийн баримт / ЗХБ материалын шалгалт."""
    corp = sorted(sols_of_branch(main, CORP_BRANCHID, DATA_END) | {OLD_SOL[0]})
    mon = sorted(corp + sorted(sols_of_branch(main, 1168, DATA_END)) + [815])   # 815 = лизинг (act_06)
    rid = 0
    for sol in mon:
        mean = rng.choice([55, 65, 72, 78, 84, 92, 97])
        for qe in _q_ends(D(2024, 1, 1), DATA_END):
            if sol == OLD_SOL[0] and qe >= REORG_DATE or sol == NEW_SOL and qe < REORG_DATE:
                continue
            rid += 1
            data["COREMIS.LOAN_MONITORING_QA"].append((rid, sol, qe, round(min(100, max(30, rng.gauss(mean, 6))), 1)))
    cid = {"COREMIS.DOC_ARCHIVE_CHECK": 0, "COREMIS.LOAN_COMMITTEE_CHECK": 0}
    for table, texts in (("COREMIS.DOC_ARCHIVE_CHECK", DOC_VIOLATIONS), ("COREMIS.LOAN_COMMITTEE_CHECK", LC_VIOLATIONS)):
        for sol in corp + [701, 702, 815, 943]:
            worst = rng.choice([1, 1, 2, 3, 4, 5])
            for qe in _q_ends(D(2024, 1, 1), DATA_END):
                if sol == OLD_SOL[0] and qe >= REORG_DATE or sol == NEW_SOL and qe < REORG_DATE:
                    continue
                for _ in range(rng.randint(1, 3)):
                    lvl = rng.randint(1, worst) if rng.random() < 0.35 else 1
                    cid[table] += 1
                    day = qe - dt.timedelta(days=int(rng.uniform(0, 80)))
                    data[table].append((cid[table], sol, day, lvl, texts[lvl]))


def _cards(rng, data, sols):
    issue_sols = [101 + i for i in range(len(RETAIL))] + [803, 886, 887, 888]
    fraud = {s: rng.choice([0.002, 0.005, 0.01, 0.02, 0.035]) for s in issue_sols}
    term = []
    for i in range(len(RETAIL)):
        for k in range(3):
            tid = f"T{101 + i}{k}"
            ttype = "ATM" if k == 0 else "POS"
            term.append(tid)
            data["CARDZONE.TERMINAL"].append((tid, 101 + i, ttype, None if ttype == "ATM" else f"Худалдаа {i}-{k}"))
    cards = []
    for cif, _, seg, sol, _ in data["FINACLE.CMG"]:
        if rng.random() < 0.6:
            isol = sol if sol in issue_sols else rng.choice(issue_sols)
            cid = f"4{len(cards) + 1:015d}"
            cards.append((cid, isol))
            data["CARDZONE.CARD"].append((cid, cif, isol, rng.choice(["Classic", "Gold", "Business", "Platinum"]),
                                          D(2022, 1, 1) + dt.timedelta(days=int(rng.uniform(0, 1200))), "ACTIVE"))
    txn = 0
    for me in _month_ends(D(2026, 1, 1), DATA_END):
        ms = me.replace(day=1)
        for cid, isol in cards:
            for _ in range(_poisson(rng, 4)):
                txn += 1
                day = ms + dt.timedelta(days=int(rng.uniform(0, (me - ms).days + 1)))
                tid = rng.choice(term)
                data["CARDZONE.CARD_TXN"].append((txn, cid, tid, day, round(rng.uniform(5e3, 2e6), 2),
                                                  "ATM" if tid.endswith("0") else rng.choice(["POS", "ECOM"]),
                                                  "Y" if rng.random() < fraud[isol] else "N"))
    data["_card_issue_sol"] = dict(cards)


def _jira(rng, data, sols):
    units = ["ББГ-Корпорейт харилцагчийн хэлтэс", "Сансар салбар", "Дархан салбар", "Төв оффис", None]
    for i in range(1, 81):
        day = D(2026, 4, 1) + dt.timedelta(days=int(rng.uniform(0, (DATA_END - D(2026, 4, 1)).days + 1)))
        data["JIRA.ABH_JIRA_NEW"].append((i, rng.choice(["Хаалга", "Сейф", "Камер"]), rng.choice(units)))
        data["JIRA.JIRAISSUE_NEW"].append((i, 1000 + i, "11457" if rng.random() < 0.8 else "10001", day))


def _knowledge(rng, data, incs, profs):
    """Мэдлэгийн шалгалт: хагас жил тутам (06-15, 12-15), тухайн өдөр ажиллаж байсан ажилтан, 5% нь өгөөгүй."""
    tid = 0
    mean = {sol: rng.uniform(76, 98) for sol in profs}
    for day in (D(2024, 6, 15), D(2024, 12, 15), D(2025, 6, 15), D(2025, 12, 15), D(2026, 6, 15)):
        for inc in incs:
            if _active(inc, day) and rng.random() > 0.05:
                tid += 1
                data["ERP.ERP_HR_KNOWLEDGE_TEST"].append(
                    (tid, inc.emp_id, day, round(min(100.0, max(40.0, rng.gauss(mean[inc.sol], 6))), 1)))


def activity_branches() -> list[int]:
    """Үйл ажиллагааны BRANCHID (config/activity_map.csv + ТОДРУУЛАХ 5 бүлгийн demo дугаар)."""
    with (ROOT / "config" / "activity_map.csv").open(encoding="utf-8-sig") as f:
        out = []
        for r in csv.DictReader(f):
            b = r["BRANCHID"] or DEMO_BRANCH.get(int(r["GROUP_NO"]))
            if b:
                out.append(int(b))
    return sorted(set(out))


def _grc(rng, data, sols):
    """GRC: дотоод аудит (+ асуудал), зайны аудит, МБ / хөндлөнгийн аудит, журам, мэдээллийн нууц."""
    eng = fid = rid = xid = did = iid = 0
    branches = activity_branches()
    never = set(rng.sample(branches, 3))                   # аудит ороогүй үйл ажиллагаа
    for b in branches:
        if b not in never:
            end = D(2026, 9, 15) - dt.timedelta(days=int(rng.uniform(5, 900)))
            if rng.random() < 0.2:
                end = D(2026, 7, 1) + dt.timedelta(days=int(rng.uniform(0, 75)))    # Q3-д аудит орсон
            ends = [end]
            if rng.random() < 0.7:
                ends.append(end - dt.timedelta(days=int(rng.uniform(450, 1000))))
            high_share, impl = rng.choice([0.05, 0.12, 0.18, 0.24, 0.35]), rng.choice([0.7, 0.82, 0.88, 0.93, 0.99])
            for e in sorted(ends):
                eng += 1
                data["GRC.AUDIT_ENGAGEMENT"].append((eng, b, e - dt.timedelta(days=int(rng.uniform(20, 60))), e,
                                                     rng.choice([1, 1, 3, 3, 5])))
                for _ in range(rng.randint(4, 12)):
                    fid += 1
                    risk = "ӨНДӨР" if rng.random() < high_share else rng.choice(["ДУНД", "БАГА"])
                    due = e + dt.timedelta(days=int(rng.uniform(30, 300)))
                    done = rng.random() < impl
                    closed = due - dt.timedelta(days=int(rng.uniform(0, 25))) if done else None
                    if done and rng.random() < 0.1:
                        closed = due + dt.timedelta(days=int(rng.uniform(5, 60)))        # хоцорч хэрэгжсэн
                    if closed and closed > DATA_END:
                        closed, done = None, False
                    data["GRC.AUDIT_FINDING"].append((fid, eng, risk, due, "ХЭРЭГЖСЭН" if closed else "НЭЭЛТТЭЙ", closed))
        worst = rng.choice([1, 1, 2, 3, 4, 5])
        for qe in _q_ends(D(2024, 1, 1), DATA_END):
            rid += 1
            code = rng.randint(1, worst) if rng.random() < 0.4 else 1
            data["GRC.REMOTE_AUDIT_CHECK"].append((rid, b, qe - dt.timedelta(days=int(rng.uniform(0, 60))), code))
        for reviewer, n, codes in (("МБ", rng.choice([0, 1, 1, 2]), [1, 2, 2, 3, 4, 5]),
                                   ("ХӨНДЛӨНГИЙН АУДИТ", rng.choice([1, 2, 2, 3]), [1, 1, 3, 5])):
            for _ in range(n):
                xid += 1
                data["GRC.EXTERNAL_REVIEW"].append((xid, b, reviewer, D(2023, 3, 1) + dt.timedelta(
                    days=int(rng.uniform(0, (DATA_END - D(2023, 3, 1)).days))), rng.choice(codes)))
        for k in range(rng.randint(2, 6)):
            did += 1
            approved = D(2016, 1, 1) + dt.timedelta(days=int(rng.uniform(0, 2500)))
            rev = approved + dt.timedelta(days=int(rng.uniform(0, max(1, (DATA_END - approved).days))))
            data["GRC.POLICY_DOCUMENT"].append((did, b, f"Журам {b}-{k + 1}", approved, rev))
    for sol in sols:
        for _ in range(_poisson(rng, 0.25)):
            iid += 1
            data["GRC.INFOSEC_INCIDENT"].append((iid, sol, D(2024, 1, 1) + dt.timedelta(
                days=int(rng.uniform(0, (DATA_END - D(2024, 1, 1)).days))), rng.choice(["БАНК", "ХАРИЛЦАГЧ"]),
                rng.choice([4, 4, 5])))
    # Action plan (Jira): үйл ажиллагаа бүрт улиралд 3–8 ажил
    item = 0
    for b in branches:
        on_time = rng.choice([0.8, 0.88, 0.93, 0.97, 1.0])
        for qe in _q_ends(D(2025, 1, 1), DATA_END):
            qs = D(qe.year, qe.month - 2, 1)
            for _ in range(rng.randint(3, 8)):
                item += 1
                due = qs + dt.timedelta(days=int(rng.uniform(0, (qe - qs).days + 1)))
                ok = rng.random() < on_time
                resolved = due - dt.timedelta(days=int(rng.uniform(0, 20))) if ok else (
                    due + dt.timedelta(days=int(rng.uniform(3, 40))) if rng.random() < 0.6 else None)
                if resolved and resolved > DATA_END:
                    resolved = None
                data["JIRA.ACTION_PLAN"].append((item, b, f"Action plan {b}-{item}", due - dt.timedelta(days=60),
                                                 due, resolved))


# ── activity_map (local demo) ─────────────────────────────────────────────────
DEMO_BRANCH = {2: 9002, 10: 9010, 11: 9011, 20: 9020, 21: 9021}


def write_activity_map(path: Path = DEMO_DIR / "activity_map.csv") -> Path:
    """config/activity_map.csv + ТОДРУУЛАХ 5 бүлэгт demo BRANCHID + аудитын огноо (local-д л)."""
    rng = random.Random(SEED + 1)
    src = list(csv.DictReader((ROOT / "config" / "activity_map.csv").open(encoding="utf-8-sig")))
    audits = [D(2024, 6, 14), D(2024, 11, 20), D(2025, 3, 10), D(2025, 6, 2), D(2025, 9, 15), D(2025, 12, 8),
              D(2026, 2, 16), D(2026, 4, 20), D(2026, 8, 3)]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(src[0].keys()))
        w.writeheader()
        for r in src:
            g = int(r["GROUP_NO"])
            if not r["BRANCHID"] and g in DEMO_BRANCH:
                r = {**r, "BRANCHID": str(DEMO_BRANCH[g]), "CONFIDENCE": "DEMO", "NOTE": "local demo-д л"}
            r["LAST_AUDIT_DATE"] = {1: "2025-04-15", 40: "2025-10-01"}.get(g) or rng.choice(audits).isoformat()
            w.writerow(r)
    return path


if __name__ == "__main__":
    import time
    t0 = time.time()
    data = build()
    for k, v in sorted(data.items()):
        if not k.startswith("_"):
            print(f"  {k:<36} {len(v):>7}")
    print(f"{time.time() - t0:.1f}s, {write_activity_map()}")
