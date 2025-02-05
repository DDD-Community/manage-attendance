FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# CMD ["gunicorn", "--bind", "unix:/tmp/gunicorn.sock", "ddd_app_server.wsgi:application"]
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ddd_app_server.wsgi:application"]
CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=24", "--worker-class=gevent", "--worker-connections=512", "--max-requests=1024", "--timeout=180", "--log-level=debug", "ddd_app_server.wsgi:application"]