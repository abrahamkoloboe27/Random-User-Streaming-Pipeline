FROM apache/airflow:slim-latest-python3.9
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
USER root
RUN apt-get update && apt-get install -y default-jre-headless procps
USER airflow




