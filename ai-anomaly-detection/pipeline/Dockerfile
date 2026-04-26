FROM python:3.11-slim

RUN apt-get update && apt-get install -y     curl ca-certificates && rm -rf /var/lib/apt/lists/*

RUN curl -LO https://dl.k8s.io/release/v1.28.0/bin/linux/amd64/kubectl     && chmod +x kubectl && mv kubectl /usr/local/bin/

WORKDIR /app
RUN mkdir -p /app/model /app/logs /app/data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .

CMD ["python", "main.py"]
