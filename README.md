# Pinterest Feed Scraper API

A lightweight Django REST API that logs into Pinterest, scrapes images from **your personal home feed**, stores them in a database and exposes convenient HTTP endpoints to consume them.

---

## ✨ Features

* **Headless Pinterest Login** – Uses [`pinterest-dl`](https://github.com/sean1832/pinterest-dl) to perform a real browser login and capture fresh cookies automatically.
* **Image Scraper** – Fetches high-quality images (src, alt text, fall-back URLs & origin) from the logged-in home feed.
* **Persistent Storage** – Saves everything to the `ImageURL` model so the same picture is never stored twice.
* **REST API** – `GET /api/home_feed/?count=N` returns a random subset of saved images, `POST /api/trigger_scraping/` runs the scraper on-demand.
* **Cron Friendly** – Background scraping command wired to `django-crontab` (default: every day at 06:00 UTC).
* **Docker Ready** – Production Dockerfile, Compose stack (Gunicorn + Nginx) and sample CI/CD workflow are included.

---

## 🖼️ Demo response

```json
{
  "message": "Images retrieved successfully",
  "total_available": 124,
  "count": 3,
  "images": [
    {
      "src": "https://i.pinimg.com/736x/...jpg",
      "alt": "Blue hour over the Alps",
      "origin": "https://www.pinterest.com",
      "fallback_urls": [
        "https://i.pinimg.com/564x/...jpg",
        "https://i.pinimg.com/236x/...jpg"
      ]
    },
    { "…": "…" }
  ]
}
```

---

## 📦 Tech stack

* Python 3.11
* Django 5 + Django REST Framework
* `pinterest-dl` (browser automation)
* SQLite (default) – easily swapped for Postgres/MySQL
* `django-crontab` (scheduler)
* Docker / Gunicorn / Nginx (production)

---

## 🔧 Local development

1. **Clone & create a virtual env**

   ```bash
   git clone https://github.com/<you>/pinterest_feed.git
   cd pinterest_feed
   python3 -m venv .venv && source .venv/bin/activate
   ```

2. **Install dependencies**

   ```bash
   pip3 install -r requirements.txt
   ```

3. **Create the `.env` file** (credentials are **never** committed):

   ```env
   ACCOUNT=your_email@example.com
   PASSWORD=your_pinterest_password
   ```

4. **Apply migrations & run**

   ```bash
   python3 manage.py migrate
   python3 manage.py runserver 0.0.0.0:8000
   ```

5. **Open** `http://localhost:8000/api/home_feed/` – you should see an empty list until you scrape ✨

---

## 🏃‍♀️ Scraping images

* **One-off (CLI)**

  ```bash
  # Scrape 30 images
  python3 manage.py scrape_images --count 30
  ```

* **One-off (API)**

  ```bash
  curl -X POST http://localhost:8000/api/trigger_scraping/ -d '{"count": 30}' -H "Content-Type: application/json"
  ```

* **Scheduled** – a crontab entry `0 6 * * *` is registered automatically; run `python3 manage.py crontab add` to enable it.

---

## 🖥️ API reference

| Method | Endpoint                       | Description                                   |
| ------ | -------------------------------- | --------------------------------------------- |
| GET    | `/api/home_feed/?count=10`      | Return up to 10 random images (max 10)        |
| POST   | `/api/trigger_scraping/`        | Body: `{ "count": 20 }` – scrape N images    |

All endpoints are open (`AllowAny`) out of the box but can be locked down with DRF settings.

---

## 🐳 Docker (production)

The repository already ships with a production-grade setup:

```bash
# Build and start (first time)
export DJANGO_SECRET_KEY=$(python - <<'PY' "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*(-_=+)') for _ in range(50)))" PY)
export ACCOUNT=your_email@example.com
export PASSWORD=your_pinterest_password

docker compose -f docker-compose.prod.yml up -d --build
```

* Gunicorn listens on port **8000** inside the `web` container
* Nginx proxies port **80 → 8000** and serves static files
* SQLite database & collected static files live in named volumes for persistence

Run migrations / collectstatic after the first boot:

```bash
docker compose -f docker-compose.prod.yml exec web python3 manage.py migrate
docker compose -f docker-compose.prod.yml exec web python3 manage.py collectstatic --noinput
```

---

## 🚀 Deployment

A complete CI/CD example for GitHub Actions (`doc/deployment_plan.md`) demonstrates zero-downtime deployments to DigitalOcean or AWS EC2. Adjust secrets & server IP and you are good to go.

---

## 🤝 Contributing

Found a bug or have an improvement idea? Feel free to open an issue or submit a pull request. Please keep the code style consistent with the existing project.

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

* [`pinterest-dl`](https://github.com/keboola/pinterest-dl) – the heavy lifting behind the scenes
* Django REST Framework – API bliss
* Unsung open-source heroes everywhere 💚 
