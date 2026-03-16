FROM python:3.10-slim

WORKDIR /app

# 1. Install Java (for Spark) AND build tools (for Pip C-extensions)
RUN apt-get update && \
    apt-get install -y default-jre build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 2. Upgrade Pip to the latest version before installing the heavy packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "-u", "main.py"]