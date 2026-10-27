FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8050
EXPOSE 8050
CMD ["sh", "-c", "gunicorn app:server --bind 0.0.0.0:${PORT:-8050} --workers 1 --threads 4 --timeout 1800"]
