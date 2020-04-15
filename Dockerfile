FROM python:3

RUN pip3 install requests prometheus_client

RUN git clone https://github.com/AndreiGavriliu/ff3-prometheus-exporter.git /opt/ff3-prometheus-exporter
WORKDIR /opt/ff3-prometheus-exporter

ENTRYPOINT ["python3", "-u", "/opt/ff3-prometheus-exporter/ff3_prometheus_exporter.py"]
