# Restaurant Ordering API Progress

Last updated: 2026-08-26

## Current Stage

The core backend MVP is complete and the project has a working production-style deployment on AWS EC2.

Live API docs:

```text
https://restohubapi.duckdns.org/api/docs/
```

Current production request flow:

```text
Browser
  -> DuckDNS domain
  -> Elastic IP
  -> EC2 Security Group
  -> Nginx container on ports 80/443
  -> Gunicorn/Django web container on port 8000
  -> RDS MySQL
```

## Completed Backend Work

- Custom email-based user model.
- User roles: platform admin, owner, waiter, and chef.
- JWT login and refresh endpoints.
- Password change endpoint with old-password verification.
- Restaurant, menu, menu item, table, order, and order-item APIs.
- Restaurant-scoped permissions and querysets.
- Serializer validation for ownership, restaurant matching, nested order items, and order totals.
- Order status workflow rules.
- Filtering, searching, ordering, and pagination.
- Swagger/OpenAPI documentation with drf-spectacular.
- XSS-style input validation for important text fields.
- Throttling/rate limits, including stricter auth endpoint throttles.
- Menu item image field and media handling.
- Automated model, serializer, permission, and API tests.

## Completed Docker Work

- Base Docker Compose file.
- Development Docker Compose file.
- Production Docker Compose file.
- Dockerfile using Python image and project requirements.
- MySQL container with health check.
- Persistent MySQL volume.
- Static and media volumes.
- Gunicorn replacing Django development server in production.
- Nginx reverse proxy in production.
- Non-root Django container user.
- Environment-based settings.
- `.env` and `.env.prod` excluded from Git.

## Completed AWS / Deployment Work

- Created Ubuntu EC2 instance.
- Connected with SSH using `.pem` key.
- Configured Security Group:
  - SSH `22` restricted to personal IP.
  - HTTP `80` public.
  - HTTPS `443` public.
  - MySQL `3306` not public.
- Installed Docker and Docker Compose on EC2.
- Allowed the `ubuntu` user to use Docker without `sudo`.
- Cloned project into `/home/ubuntu/apps/resturantordering`.
- Created production `.env.prod` on the EC2 only.
- Deployed with Docker Compose.
- Added 2GB swap because `t3.micro` RAM was too low and MySQL was killed by the OS.
- Attached Elastic IP: `3.77.252.67`.
- Added free DuckDNS domain: `restohubapi.duckdns.org`.
- Generated HTTPS certificate using Certbot and Let's Encrypt.
- Configured Nginx HTTP -> HTTPS redirect.
- Configured Nginx to serve HTTPS on port `443`.
- Added cron job for automatic certificate renewal.
- Created RDS MySQL database:
  - DB instance identifier: `restaurant-ordering-db`.
  - Database name: `restaurant_ordering`.
  - Master username: `restaurant_admin`.
  - Endpoint: `restaurant-ordering-db.c7o2cwuyubs3.eu-central-1.rds.amazonaws.com`.
- Configured RDS security group to allow MySQL `3306` from the EC2 security group only.
- Updated production database environment to use RDS instead of Docker service `db`.
- Fixed production `DB_HOST` override in Docker Compose so the web container receives the RDS endpoint from `.env.prod`.
- Fixed `DB_NAME` typo from `restaurant-ordering` to `restaurant_ordering`.
- Ran Django migrations successfully against RDS.
- Added Django HTTPS proxy settings:
  - `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`
  - `USE_X_FORWARDED_HOST = True`
- Passed production security environment variables into the `web` container:
  - `CORS_ALLOWED_ORIGINS`
  - `CSRF_TRUSTED_ORIGINS`
  - `SECURE_SSL_REDIRECT`
  - `SESSION_COOKIE_SECURE`
  - `CSRF_COOKIE_SECURE`
  - HSTS settings

## Important Verification Already Seen

- Docker containers reached healthy/running state:
  - `db`
  - `web`
  - `nginx`
- Swap became active:

```text
Swap: 2.0Gi
```

- HTTPS certificate was successfully issued for:

```text
restohubapi.duckdns.org
```

- Certificate expiry shown by Certbot:

```text
2026-11-23
```

- Live HTTPS docs worked:

```text
https://restohubapi.duckdns.org/api/docs/
```

- RDS connection worked after fixing `DB_HOST` and `DB_NAME`.
- Django migrations were applied successfully on the RDS database.
- Production web container stayed up after switching to RDS.

## Important Bugs / Lessons From Deployment

### Docker env flow

Production values move through three layers:

```text
.env.prod
  -> docker-compose.prod.yml web.environment
  -> Django settings.py config(...)
```

If a value exists in `.env.prod` but is not passed under `web.environment`, Django may not see it inside the container.

### RDS DB_HOST issue

`.env.prod` had the RDS endpoint, but Docker Compose had hardcoded:

```yaml
DB_HOST: db
```

That forced Django to keep using the old MySQL Docker container.

Correct production style:

```yaml
DB_HOST: ${DB_HOST:?DB_HOST must be set}
```

### RDS DB_NAME issue

Wrong:

```env
DB_NAME=restaurant-ordering
```

Correct:

```env
DB_NAME=restaurant_ordering
```

The hyphen version caused:

```text
Unknown database 'restaurant-ordering'
```

### HTTPS redirect loop issue

Nginx receives public HTTPS, decrypts it, then forwards internal HTTP to Django:

```text
Browser --HTTPS--> Nginx --HTTP--> Django
```

Without `SECURE_PROXY_SSL_HEADER`, Django may think the original request was HTTP. With `SECURE_SSL_REDIRECT=True`, that can cause:

```text
ERR_TOO_MANY_REDIRECTS
```

Fix:

```python
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
```

## Main Local Development Commands

Start development:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

Run tests:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T web python manage.py test
```

Stop development without deleting database data:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
```

Local Swagger:

```text
http://127.0.0.1:8000/api/docs/
```

## Main EC2 Production Commands

Go to project:

```bash
cd /home/ubuntu/apps/resturantordering
```

Start/recreate production containers:

```bash
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Check containers:

```bash
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml ps
```

Check web logs:

```bash
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml logs --tail=80 web
```

Check nginx logs:

```bash
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml logs --tail=80 nginx
```

Check memory:

```bash
free -h
```

Check swap persistence:

```bash
tail -n 5 /etc/fstab
```

## Remaining Work

Recommended next big topic:

```text
RDS cleanup
```

Why: The app is now using RDS, but the Docker MySQL container/service still exists in production Compose. It should be removed or disabled from production once RDS is fully confirmed.

Other remaining topics:

1. Remove/disable Docker MySQL from production Compose.
2. Fix MySQL Strict Mode warning for RDS.
3. Create production superuser again because RDS is a fresh database.
4. S3 for uploaded menu item images.
5. ECR for Docker images.
6. CloudWatch for logs, metrics, and alarms.
7. Secrets Manager or SSM Parameter Store.
8. CI/CD with GitHub Actions.
9. Backups and restore strategy.
10. Optional Redis/caching after measuring useful endpoints.
11. Optional Load Balancer, ACM, CloudFront, and scaling.
