FROM mcr.microsoft.com/playwright:v1.56.1-noble

WORKDIR /scraper

COPY package.json package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund

COPY scrape.mjs scrape.test.mjs ./

CMD ["node", "scrape.mjs"]
