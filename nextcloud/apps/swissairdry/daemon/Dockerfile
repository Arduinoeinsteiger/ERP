FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy daemon code
COPY daemon.py .

# Default environment variables
ENV APP_ID=swissairdry \
    APP_VERSION=1.0.0 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8081 \
    APP_SECRET=change_me_in_production \
    NEXTCLOUD_URL=http://nextcloud \
    API_URL=http://api:5000 \
    SIMPLE_API_URL=http://simple-api:5001 \
    MQTT_BROKER=mqtt \
    MQTT_PORT=1883 \
    MQTT_WS_PORT=9001

# Expose the port for the API
EXPOSE 8081

# Run the daemon
CMD ["python", "daemon.py"]