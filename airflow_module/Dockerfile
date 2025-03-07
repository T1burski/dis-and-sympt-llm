FROM apache/airflow:2.10.2

USER airflow

ENV AIRFLOW_HOME=/opt/airflow/airflow_module

WORKDIR /opt/airflow/airflow_module

COPY requirements.txt /opt/airflow/airflow_module/requirements.txt

RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt
