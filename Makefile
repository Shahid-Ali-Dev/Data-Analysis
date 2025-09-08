.PHONY: fmt lint ingest features train forecast app mlflow

fmt:
	black src/ app/ tests/
	ruff check --fix .

lint:
	ruff check .

ingest:
	python -m bmi.etl.ingest --sample

features:
	python -m bmi.features.build_features

train:
	python -m bmi.models.train

forecast:
	python -m bmi.models.forecast

app:
	streamlit run app/streamlit_app.py

mlflow:
	mlflow ui --backend-store-uri $(or $(BMI_MLFLOW_TRACKING_URI),./mlruns)
