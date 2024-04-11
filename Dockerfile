FROM python:3.10

WORKDIR /app

COPY requirements_dev.txt .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements_dev.txt

COPY . .

CMD ["python", "-m", "app.main"]