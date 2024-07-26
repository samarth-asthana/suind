FROM python:3.9-alpine

WORKDIR /app

RUN apk add --no-cache \
    gdal-dev \
    gcc \
    musl-dev \
    g++ \
    libffi-dev \
    openssl-dev

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn pydantic requests geojson rasterio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
