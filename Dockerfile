FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl fonts-dejavu-core fonts-dejavu-extra \
    && mkdir -p /usr/share/fonts/truetype/antonio \
    && curl -fsSL 'https://raw.githubusercontent.com/google/fonts/main/ofl/antonio/Antonio%5Bwght%5D.ttf' -o /usr/share/fonts/truetype/antonio/Antonio\[wght\].ttf \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir Pillow PyYAML

COPY . .

CMD ["python", "tools/build_poster.py"]
