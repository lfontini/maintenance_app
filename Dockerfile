FROM ubuntu:20.04

ENV TZ=America/Sao_Paulo
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    iputils-ping \
    gcc \
    libpq-dev \
    tzdata \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependências Python
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Código da aplicação
COPY . .

EXPOSE 8000

RUN chmod +x start.sh start_celery.sh start_celery_beat.sh wait_for_db.sh

