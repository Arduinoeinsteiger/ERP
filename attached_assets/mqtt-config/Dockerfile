FROM alpine:3.17

RUN apk --no-cache add bash mosquitto-clients

WORKDIR /app

COPY update_mqtt_config.sh /app/
RUN chmod +x /app/update_mqtt_config.sh

ENTRYPOINT ["/app/update_mqtt_config.sh"]