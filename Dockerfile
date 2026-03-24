FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY web/ ./web/
COPY data/ ./data/ 2>/dev/null || true

ENV PORT=5000
ENV FLASK_DEBUG=false

EXPOSE 5000

CMD ["python", "web/app.py"]
