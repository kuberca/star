FROM python:3.8

WORKDIR /star

COPY model model
COPY __init__.py __init__.py
COPY backend backend
COPY config config
COPY containerd containerd
COPY datasource datasource
COPY drain3.ini drain3.ini
COPY feedback feedback
COPY label label
COPY main.py main.py
COPY predictor predictor
COPY prep  prep
COPY sems sems
COPY setup.py setup.py
COPY requirements.txt requirements.txt
COPY storage storage
COPY results results
COPY web web
COPY fb.csv fb.csv

RUN pip install -r requirements.txt

EXPOSE 5000/tcp

ENTRYPOINT ["python", "main.py"]
