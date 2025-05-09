FROM python:3.11-slim

RUN apt-get update && apt-get install -y wget gnupg curl unzip fonts-liberation libnss3 libatk-bridge2.0-0 libgtk-3-0 libxss1 libasound2 libx11-xcb1 libxcb-dri3-0 libdrm2 libxdamage1 libxrandr2 libgbm1 libxshmfence1 libxcomposite1 libxfixes3 libxrender1 libxext6 libegl1 libgl1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install --with-deps

COPY . .

EXPOSE 10000

CMD ["uvicorn", "scraper_api:app", "--host", "0.0.0.0", "--port", "10000"]
