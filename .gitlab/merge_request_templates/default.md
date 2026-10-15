## Юу хийсэн
- Activity: ACT_XX
- Үзүүлэлтүүд: RI_XX_NNN, ...
- Төрөл: шинэ / засвар / runner

## Тайлбар
<!-- Томьёо, бизнес логик, яагаад ингэж хийсэн -->

## Хөгжүүлэгчийн шалгалт
- [ ] `python ri.py check -a ACT_XX` — 0 алдаа
- [ ] `python ri.py run --env dev -i ... --dry-run` — DRY_RUN_OK
- [ ] `python ri.py run --env dev -i ... --test-dates --save-csv` — SUCCESS/WARNING
- [ ] CSV-ээс 1–2 салбарыг гараар тулгасан
- [ ] Дата байхгүй огноо, хуваарь 0 үед алдаа гарахгүй (NULLIF)
- [ ] Үр дүн салбар бүрт нэг мөр: `BRANCH_ID`, `SCALE` (`show`-оор харсан)
- [ ] Давхцах кодыг `shared/`-ээс иш татсан (sol → branch нь `{{shared.branch_sol}}`)
- [ ] YAML: description, source_tables, test_dates бөглөсөн, status = REVIEW

## Dev run үр дүн
```
(python ri.py run ... -ийн хураангуй хүснэгтийг энд хуулна)
```

## Reviewer шалгах зүйл
- [ ] Томьёо нь description-тэй таарч байна
- [ ] Join-оос мөр үржихгүй (давхардал алга)
- [ ] Хуучин procedure-ийн үр дүнтэй 2–3 салбараар тулгасан
- [ ] Огнооны filter зөв (:p_date_from / :p_date_to)
- [ ] Reviewer өөрөө dev дээр ажиллуулж үр дүнг харсан
