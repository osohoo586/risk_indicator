"""Risk indicators — prod Airflow DAG (Airflow 3).

Prod серверийн Airflow-ийн dags/ folder-т хуулна. Өдөр бүр 07:00-д:

    python ri.py auto --env prod --all

`auto` нь сүүлийн 1 жилийн (--since) үзүүлэлт бүрийн frequency-ийн тайлант огноонуудаас ClickHouse-ийн ri_result-д
дутуу (ШИНЭ: шинэ үе, шинэ файл, өмнө нь source бэлэн биш), сүүлийн оролдлого нь алдаатай (АЛДАА), SQL / нийтлэг
тооцоолол / shared / params өөрчлөгдсөн (ӨӨРЧЛӨГДСӨН), эсвэл dependency нь дахин ажиллах (ХАМААРАЛ) үзүүлэлтийг л
ажиллуулж, хөндөгдсөн үйл ажиллагааны нийт оноог дахин тооцно. Гарын үнэлгээ (manual) орохгүй — ri.py manual load.
Бүгд бичигдсэн бол юу ч хийхгүй — тиймээс өдөр бүр ажиллуулахад аюулгүй, алдсан өдрийг дараагийн өдөр өөрөө нөхнө.
Аль нэг үзүүлэлт алдаа өгвөл task FAILED болно (бусад нь бичигдсэн хэвээр); дараагийн өдрийн `auto` дахин оролдоно.
prod-д зөвхөн status TESTED / DONE үзүүлэлт ажиллана (config/prod.yaml min_status).
Юу ажиллахыг харах: python ri.py auto --env prod --all --plan
Урт хугацааг нөхөх:  python ri.py auto --env prod --all --since 2026-01-01
"""
import os
from datetime import datetime

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

RI_HOME = os.environ.get("RI_HOME", "/opt/risk_indicators")   # git clone хийсэн газар (.venv, .env-тэй)

with DAG(
    dag_id="risk_indicators",
    schedule="0 7 * * *",
    start_date=datetime(2026, 10, 1),
    catchup=False,
    max_active_runs=1,
    tags=["risk", "clickhouse"],
) as dag:
    BashOperator(
        task_id="auto_run_indicators",
        bash_command=f"cd {RI_HOME} && .venv/bin/python ri.py auto --env prod --all",
    )
