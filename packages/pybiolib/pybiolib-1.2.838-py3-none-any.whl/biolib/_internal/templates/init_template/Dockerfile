FROM python:3.13.3-slim
WORKDIR /home/biolib/

COPY run.sh .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src .

RUN mkdir output
