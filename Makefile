.PHONY: install quality seed dbt analytics clean

install:
	python -m pip install -e '.[dev]'

quality:
	ruff check src scripts tests
	pytest
	python scripts/check_snapshot_quality.py

seed:
	python scripts/export_warehouse_seed.py

dbt:
	mkdir -p analytics/warehouse
	dbt deps --project-dir analytics --profiles-dir analytics
	dbt build --project-dir analytics --profiles-dir analytics

analytics: seed quality dbt

clean:
	dbt clean --project-dir analytics --profiles-dir analytics
	rm -f analytics/warehouse/financial_analytics.duckdb
