FROM python:3.11-slim

# set working directory
WORKDIR /app

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# install python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY .env.example .env

# default entrypoint: run or serve based on ENV
ENV ENTRYPOINT_MODE=run
ENTRYPOINT ["sh", "-c", "if [ \"$ENTRYPOINT_MODE\" = \"serve\" ]; then mail-maestro serve; else mail-maestro run; fi"]