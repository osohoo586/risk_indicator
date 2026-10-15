# shared/ — олон SQL-д давхцдаг хэсэг

Хоёр ба түүнээс олон SQL-д (үзүүлэлт, нийтлэг тооцоолол `activities/_shared/sh_NNN.sql`, runner) ижил хэсэг
(бүтэц, идэвхтэй ажилтан, зээлийн багц г.м.) байвал энд НЭГ удаа бичиж, иш татна:

```sql
FROM   {{shared.erp.sol_flow}} f            -- shared/erp/sol_flow.sql
JOIN   {{shared.erp.employee_sol}} e        -- shared/erp/employee_sol.sql
```

Runner `{{shared.x}}`-ийг файлын SELECT-ээр (хаалтанд) солино. Shared файл дотроо өөр `{{shared.y}}`,
`{{schema.x}}`, `:p_report_date` зэрэг параметр ашиглаж болно.

**`shared/` ба `activities/_shared/`-ийн ялгаа:** `shared/*.sql` нь SQL-ийн *хэсэг* (дэд SELECT) — өөрөө
үр дүн бичихгүй. `activities/_shared/sh_NNN.sql` нь *бүтэн тооцоолол* (ENTITY_LEVEL, ENTITY_ID, VALUE …) —
олон үйл ажиллагааны үзүүлэлт (`calc: SH_NNN`) нэг тооцооллын SOL мөрийг өөр өөрийн SOL-уудаар нэгтгэнэ.

## Нэрлэх стандарт

| Дүрэм | Жишээ |
|---|---|
| Зөвхөн жижиг үсэг, тоо, `_` | `units.sql` |
| Эх системээр folder: `org/`, `erp/`, `finacle/`, `coremis/`, `cardzone/` | `erp/employee_sol.sql` → `{{shared.erp.employee_sol}}` |
| Нэр нь юу буцаахыг хэлнэ (нэгж + агуулга) | `erp/sol_flow.sql`, `finacle/loan_book.sql` |
| Зөвхөн нэг SELECT (procedure блок, DML биш), `SELECT *` хориглоно | |
| Эхний мөрүүдэд comment: юу буцаадаг, баганууд, хэн ашигладаг | |

`python ri.py check` нь иш татсан файл байгаа эсэх, стандарт, хэрэглэгдээгүй файлыг шалгана.
`shared/`-ийн өөрчлөлт олон үзүүлэлтэд нөлөөлөх тул тусдаа MR-ээр хийнэ.

## Одоо байгаа (баганын нэр ТААМАГ — бодит нэр өөр бол ЗӨВХӨН эдгээрийг засна)

| Файл | Буцаах | Ашигладаг |
|---|---|---|
| `org/units.sql` | SOLID, BRANCHID, SOLNAME (COREMIS.MAIN, тайлант өдрийн snapshot) | runner (config `org`), RI_40_1526, ACTIVITY түвшний нийтлэг SQL |
| `erp/employee_sol.sql` | тайлант өдөр ажиллаж буй ажилтан: EMPLOYEE_ID, SOLID, POSITION_NAME, IS_MANAGER, HIRE_DATE, POSITION_START | SH_001, 002, 004, 005, 006, 022, RI_40_1526 |
| `erp/sol_flow.sql` | SOLID бүрийн HC_START, HC_END, SEPARATIONS (+ удирдах `_MGR`) | SH_007, RI_40_1519, RI_40_1520 |
| `finacle/loan_book.sql` | зээлийн данс: SOL_ID, CLASS_CODE, OUTSTANDING_AMT, PROVISION_AMT, IS_GREEN | SH_009, SH_034 … SH_036 |
| `grc/last_audit.sql` | тайлант өдрөөс өмнөх сүүлийн дотоод аудит: BRANCHID, ENGAGEMENT_ID, LAST_AUDIT_DATE, RATING_CODE | SH_017 … SH_020, runner (config `audit:`) |
