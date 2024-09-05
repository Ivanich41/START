FROM python:3.9-alpine

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt && \
    chmod 600 /app/registry_key

CMD ["python3", "-u", "main_C.py"]
