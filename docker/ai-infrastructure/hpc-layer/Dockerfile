FROM nvcr.io/nvidia/rapids-pb24h1:24.02.06-runtime

USER root

RUN apt-get update && apt-get install -y python3.9 python3-pip

WORKDIR /app

COPY ./hpc-service/requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./hpc-service /app

CMD ["python3", "data_processing.py"] 