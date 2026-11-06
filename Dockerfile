FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends fonts-dejavu-core fonts-dejavu-extra librsvg2-bin \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir Pillow PyYAML

COPY . .

CMD ["python", "tools/build_graphics.py"]
