FROM python:3.11-slim

WORKDIR /app

COPY udp_server.py /app/udp_server.py

EXPOSE 12345/udp

CMD ["python", "udp_server.py"]

