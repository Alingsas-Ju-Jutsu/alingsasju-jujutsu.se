FROM ruby:3.3-slim

WORKDIR /app

ENV BUNDLE_JOBS=4 \
    BUNDLE_RETRY=3

COPY Gemfile Gemfile.lock ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential python3-pil python3-yaml fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/* \
    && bundle install

COPY . .

EXPOSE 4000 35729

CMD ["sh", "-c", "python3 tools/build_poster.py && exec bundle exec jekyll serve --host 0.0.0.0 --livereload --force_polling"]
