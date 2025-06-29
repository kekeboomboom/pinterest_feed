# Nginx + HTTPS Setup Plan for `pin.keboom.ac`

> Goal: Serve the Django app running in the `pinterest_feed-web` Docker container (listening on port **8000**) over HTTPS at **https://pin.keboom.ac** using Nginx acting as a reverse-proxy.

---

## 1. Prerequisites

1. **SSH access** to the cloud server with a sudo-capable user.
2. **Public IPv4 address** of the server (e.g., `18.222.xxx.xxx`).
3. **DNS control** for the domain `keboom.ac` (e.g., Cloudflare, Route 53, Namecheap, etc.).
4. **Docker container** `pinterest_feed-web` already running and exposing port `8000` (confirmed via `docker ps`).
5. Outbound 80/443 access on the server (required for Let's Encrypt challenges and package installs).

## 2. High-Level Steps

1. Point the sub-domain `pin.keboom.ac` to the server IP (A record).
2. Install Nginx from the distro package repo.
3. (Optional) Configure UFW / firewalld / AWS Security Group to allow ports 80 & 443.
4. Obtain a free TLS certificate from Let's Encrypt using **Certbot**.
5. Create an Nginx site configuration that:
   * Listens on 80 → redirects all traffic to 443.
   * Listens on 443 with the issued certificate.
   * Proxies requests to `http://127.0.0.1:8000` (the Django container).
6. Enable the site, test the config, and reload Nginx.
7. Set up automatic certificate renewal.
8. Validate with an end-to-end smoke test (`curl -I https://pin.keboom.ac/health/`).
9. (Optional) Harden Nginx (security headers, rate limiting, logging).

## 3. Detailed Procedure

### 3.1 DNS Configuration

1. Go to your DNS provider for `keboom.ac`.
2. Add an **A record**:
   * **Name**: `pin`
   * **Type**: `A`
   * **Value**: `<SERVER_PUBLIC_IP>`
   * **TTL**: 5 min (for quick propagation during setup)
3. Wait until `dig pin.keboom.ac` (from your local machine) resolves to the server IP.

### 3.2 Install Nginx & Certbot (Ubuntu 24.04 LTS)

```bash
sudo apt update
sudo apt install -y nginx python3-certbot-nginx

# Enable & start Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 3.3 Firewall / Security Group

* **AWS SG:** Ensure inbound rules for TCP 80 & 443 from `0.0.0.0/0` (or locked further) are allowed.
* **UFW (Ubuntu):**
  ```bash
  sudo ufw allow 80,443/tcp
  sudo ufw reload
  ```

### 3.4 Obtain TLS Certificate with Certbot

Run the interactive Certbot plugin for Nginx:
```bash
sudo certbot --nginx -d pin.keboom.ac --non-interactive --agree-tos \
  --redirect --hsts --staple-ocsp -m keboom777@gmail.com
```
This will:
* Perform the HTTP-01 challenge on port 80.
* Install the certificate files.
* Automatically create a 443 server block with SSL directives.
* Force redirect HTTP → HTTPS.

### 3.5 Custom Nginx Site (if Certbot didn't create it)

Create `/etc/nginx/sites-available/pin.keboom.ac`:
```nginx
server {
    listen 80;
    server_name pin.keboom.ac;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name pin.keboom.ac;

    ssl_certificate     /etc/letsencrypt/live/pin.keboom.ac/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pin.keboom.ac/privkey.pem;
    include             /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;

    # Increase proxy buffers for large images if needed
    client_max_body_size 20M;

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto https;
    }
}
```
Enable the site & reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/pin.keboom.ac /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 3.6 Automatic Renewal Test

Certbot installs a systemd timer/cron; verify:
```bash
sudo certbot renew --dry-run
```

### 3.7 Validation

1. Browser → `https://pin.keboom.ac` should show the Pinterest feed homepage.
2. Check SSL grade: https://www.ssllabs.com/ssltest/ (expect A or A+).
3. Logs:
   * `sudo tail -f /var/log/nginx/access.log /var/log/nginx/error.log`

### 3.8 Rollback / Removal

* Disable site: `sudo rm /etc/nginx/sites-enabled/pin.keboom.ac && sudo systemctl reload nginx`.
* Remove certificate: `sudo certbot delete --cert-name pin.keboom.ac`.

---

## 4. Useful Commands / Cheatsheet

| Purpose | Command |
|---------|---------|
| Nginx syntax check | `sudo nginx -t` |
| Show running containers | `docker ps --format "table {{.Names}}\t{{.Ports}}"` |
| Reload Nginx | `sudo systemctl reload nginx` |
| Force certificate renewal | `sudo certbot renew --force-renewal` |

---

## 5. Next Steps (after approval)

1. Execute the steps on the server (can be automated via Ansible).
2. Push the final Nginx config into version control under `infra/` for reproducibility.
3. Optionally set up **Fail2ban** and **CrowdSec** for basic intrusion protection.
4. Integrate a CI/CD pipeline (GitHub Actions) to rebuild & redeploy the Docker image when the Django app is updated.

---

*Last updated: {{DATE}}* 
