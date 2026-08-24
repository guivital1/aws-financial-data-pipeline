"""Airflow DAG for the reproducible local analytics workflow.

Mount this repository at /opt/airflow/project in an Airflow worker. The same
commands are intentionally available through the Makefile and CI.
"""

from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT = "/opt/airflow/project"

with DAG(
    dag_id="financial_data_product",
    description="Validate BCB data and publish dimensional analytics models",
    start_date=datetime(2026, 1, 1),
    schedule="0 22 * * 1-5",
    catchup=False,
    max_active_runs=1,
    tags=["data-engineering", "bcb", "portfolio"],
) as dag:
    export_seed = BashOperator(
        task_id="export_warehouse_seed",
        bash_command=f"cd {PROJECT} && python scripts/export_warehouse_seed.py",
    )
    test_python = BashOperator(
        task_id="test_python_and_quality",
        bash_command=f"cd {PROJECT} && pytest",
    )
    build_models = BashOperator(
        task_id="build_dimensional_models",
        bash_command=f"cd {PROJECT} && dbt deps --project-dir analytics --profiles-dir analytics "
        f"&& dbt build --project-dir analytics --profiles-dir analytics",
    )

    export_seed >> test_python >> build_models
