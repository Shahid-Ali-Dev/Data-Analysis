from prefect import flow, task
import subprocess

@task
def task_ingest():
    subprocess.run(["python", "-m", "bmi.etl.ingest", "--sample"], check=True)

@task
def task_features():
    subprocess.run(["python", "-m", "bmi.features.build_features"], check=True)

@task
def task_train():
    subprocess.run(["python", "-m", "bmi.models.train"], check=True)

@task
def task_forecast():
    subprocess.run(["python", "-m", "bmi.models.forecast"], check=True)

@flow
def daily_pipeline():
    task_ingest()
    task_features()
    task_train()
    task_forecast()

if __name__ == "__main__":
    daily_pipeline()
