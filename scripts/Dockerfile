FROM python:3.11-slim

WORKDIR /app

COPY scripts/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ ./scripts/

ENV PORT=8000
EXPOSE 8000

CMD ["python", "scripts/vcf_qr_generator.py", "--serve", "--port", "8000"]

