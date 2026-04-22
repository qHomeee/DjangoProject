FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создаём папки заранее и собираем статику для production-подобной проверки.
RUN mkdir -p /app/staticfiles /app/static && \
    DJANGO_SECRET_KEY=build-dummy-key python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn sneaker_store.wsgi:application --bind 0.0.0.0:${PORT:-8080}"]
