FROM python:3.11-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y gcc python3-dev build-essential \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /usr/src/app

# Update python deps
RUN pip install -U pip wheel

# Copy requirements
COPY requirements.txt /usr/src/app/

# Install project requirements
RUN pip install -r requirements.txt --no-cache-dir

# Copy directory
COPY . /usr/src/app/

# Set default starting command
CMD ["python", "run.py"]
