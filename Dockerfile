# Dockerfile
FROM python:3.12

WORKDIR /app

# Install system dependencies (including pkg-config)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the project files into the container
COPY . .

# Make start.sh executable
RUN chmod +x /app/start.sh

EXPOSE 8000

# Run the start.sh script to ensure migrations and server start
CMD ["/app/start.sh"]
