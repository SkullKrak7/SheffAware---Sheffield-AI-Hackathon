FROM python:3.13-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gdal-bin libgdal-dev python3-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.headless=true", "--server.port=8501", "--server.enableCORS=false"]