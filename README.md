# Alingsås Ju-Jutsu

Jekyll site for GitHub Pages, configured for `https://alingsasju-jutsu.se`.

## Local development with Docker

Install Docker with the Compose plugin and GNU Make, then start the live-reloading
development server:

```sh
make serve
```

Open [http://localhost:4000](http://localhost:4000). The project directory is
mounted into the container, so changes are picked up automatically. Stop the
server with `Ctrl+C` or `make stop`.

Build the static site into `_site/` or remove generated output with:

```sh
make build
make clean
```

The site is built and deployed by the GitHub Actions workflow in
`.github/workflows/pages.yml`. In the repository settings, set Pages' build and
deployment source to **GitHub Actions**.

The initial homepage is a content-safe scaffold. The existing club site was
unavailable during setup, so its training, contact, and organization details
have not been copied or guessed.
