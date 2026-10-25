FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home appuser

COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser templates/ ./templates/

USER appuser

EXPOSE 5010

CMD ["gunicorn", "--bind", "0.0.0.0:5010", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
