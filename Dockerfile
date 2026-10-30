FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8050
EXPOSE 8050
CMD ["sh", "-c", "exec gunicorn app:server --bind 0.0.0.0:${PORT:-8050} --worker-class sync --workers 1 --threads 1 --timeout 1800"]
