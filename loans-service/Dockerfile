FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
# Genera/aplica migraciones al arrancar (esqueleto). Luego de la primera corrida local, commitea library/migrations/0001_initial.py
CMD ["sh", "-c", "python manage.py makemigrations library --noinput && python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
