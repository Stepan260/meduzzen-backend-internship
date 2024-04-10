FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install psycopg2-binary
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . .

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--proxy-headers", "--reload"]