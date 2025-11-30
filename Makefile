PY := python

.PHONY: run test small big charts memo docs ci-local fmt lint clean

install:
	$(PY) -m pip install -r requirements.txt

run:
	$(PY) scripts/run_pipeline.py

small:
	$(PY) scripts/switch_data_scale.py small && $(PY) scripts/run_pipeline.py

big:
	$(PY) scripts/switch_data_scale.py big && $(PY) scripts/run_pipeline.py

test:
	$(PY) -m pytest -q

charts:
	$(PY) scripts/make_wau_chart.py || true
	$(PY) scripts/make_cohort_heatmap.py || true
	$(PY) scripts/make_opac_chart.py || true
	$(PY) scripts/make_rev_per_wau_chart.py || true
	$(PY) scripts/make_opac_channel_bar_latest.py || true
	$(PY) scripts/make_wau_control_chart.py || true
	$(PY) scripts/make_refund_rate_chart.py || true

memo:
	$(PY) scripts/make_decision_memo.py

docs:
	$(PY) scripts/gen_metrics_doc.py

ci-local:
	$(PY) scripts/switch_data_scale.py small || true
	$(PY) scripts/run_pipeline.py
	$(PY) -m pytest -q

fmt:
	$(PY) -m black scripts tests

lint:
	$(PY) -m ruff check scripts tests

clean:
	rm -rf data/interim/*
