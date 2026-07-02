# Task: Refactor Project to Support Configurable Base URLs and Environment-Based Deployment

## Objective

Refactor the entire application so that no frontend or backend code contains hardcoded URLs, ports, hosts, or protocol values.

The application must be fully configurable through environment variables.

The system must support:

* Local development
* Docker development
* LAN deployment
* VPS deployment
* Production deployment
* Reverse proxy deployment (Nginx, Traefik, Caddy)
* HTTPS domains

without requiring source code modifications.

---

# Current Problem

The project currently assumes:

```text
http://localhost:8000
```

and serves frontend pages using hardcoded localhost references.

This is unacceptable for production.

All URLs, ports, and hosts must be environment-driven.

---

# Required Changes

## 1. Create Centralized Configuration System

Create:

```text
backend/app/core/config.py
```

Use:

```python
from pydantic_settings import BaseSettings
```

Create:

```python
class Settings(BaseSettings):
```

Required environment variables:

```env
APP_NAME=CodelessAI Smart Editor

APP_ENV=development

HOST=0.0.0.0

PORT=8000

PUBLIC_BASE_URL=http://localhost:8000

API_PREFIX=/api

FRONTEND_URL=http://localhost:8000

STATIC_URL=/static

ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

ENABLE_HTTPS=false

```

Export:

```python
settings = Settings()
```

---

# 2. Remove All Hardcoded URLs

Search entire repository.

Replace every occurrence of:

```text
localhost
127.0.0.1
http://localhost:8000
```

with dynamic configuration values.

Examples:

BAD:

```javascript
fetch("http://localhost:8000/api/edit/start")
```

GOOD:

```javascript
fetch(`${window.APP_CONFIG.API_BASE_URL}/edit/start`)
```

---

# 3. Backend URL Generation

Anywhere backend returns URLs:

BAD:

```python
return {
    "url": f"http://localhost:8000/uploads/{filename}"
}
```

GOOD:

```python
return {
    "url": f"{settings.PUBLIC_BASE_URL}/uploads/{filename}"
}
```

---

# 4. Frontend Runtime Configuration

Create:

```text
frontend/config.js
```

Example:

```javascript
window.APP_CONFIG = {
    BASE_URL: window.location.origin,
    API_BASE_URL: `${window.location.origin}/api`,
    STATIC_BASE_URL: `${window.location.origin}/static`
};
```

Every frontend API call must use:

```javascript
window.APP_CONFIG.API_BASE_URL
```

Never hardcode URLs.

---

# 5. Dynamic API Service Layer

Create:

```text
frontend/js/services/api.js
```

Example:

```javascript
const API_BASE = window.APP_CONFIG.API_BASE_URL;

export async function apiFetch(path, options = {}) {
    return fetch(`${API_BASE}${path}`, options);
}
```

All pages must use this service.

Examples:

```javascript
apiFetch("/jobs");
apiFetch("/edit/start");
apiFetch("/history");
```

---

# 6. Support Reverse Proxies

Application must work correctly behind:

* Nginx
* Traefik
* Caddy
* Cloudflare Tunnel

Enable:

```python
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
```

Trust forwarded headers.

Support:

```text
X-Forwarded-Proto
X-Forwarded-Host
```

Generate URLs accordingly.

---

# 7. Docker Improvements

Modify Docker startup.

Do not hardcode:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Use:

```bash
uvicorn app.main:app \
    --host ${HOST} \
    --port ${PORT}
```

Read values from environment.

---

# 8. Docker Compose

Expose configurable ports.

Example:

```yaml
ports:
  - "${PORT}:${PORT}"
```

Environment:

```yaml
environment:
  HOST: ${HOST}
  PORT: ${PORT}
  PUBLIC_BASE_URL: ${PUBLIC_BASE_URL}
```

---

# 9. Update FastAPI Startup

In:

```python
main.py
```

Read:

```python
settings.HOST
settings.PORT
```

Use throughout application.

---

# 10. Add Multiple Example Environments

Create:

```text
.env.development
.env.production
.env.staging
```

Examples:

Development:

```env
APP_ENV=development
HOST=0.0.0.0
PORT=8000
PUBLIC_BASE_URL=http://localhost:8000
```

Production:

```env
APP_ENV=production
HOST=0.0.0.0
PORT=8000
PUBLIC_BASE_URL=https://app.codelessai.com
```

LAN:

```env
PUBLIC_BASE_URL=http://192.168.1.100:8000
```

---

# 11. Frontend Navigation

Replace:

BAD:

```javascript
window.location.href = "http://localhost:8000/dashboard.html";
```

GOOD:

```javascript
window.location.href =
    `${window.APP_CONFIG.BASE_URL}/dashboard.html`;
```

---

# 12. Static Asset Loading

Ensure CSS, JS, images, uploads, generated images, masks, thumbnails all use relative paths.

Example:

GOOD:

```html
<script src="/js/dashboard.js"></script>
```

or

```html
<img src="/uploads/example.png">
```

Never:

```html
<script src="http://localhost:8000/js/dashboard.js">
```

---

# 13. Production Goal

After implementation, the same Docker image should work unchanged in all environments:

```text
docker run image
```

Local:

```text
http://localhost:8000
```

LAN:

```text
http://192.168.1.100:8000
```

Production:

```text
https://app.codelessai.com
```

Only the .env file should change.

No code modifications should be required.
