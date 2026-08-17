# Restaurant Ordering API Progress

## Current Stage

The core backend MVP and Docker development environment are complete. The project is now moving into production hardening and deployment work.

## Completed

- Custom email-based user model and roles: platform admin, owner, waiter, and chef.
- JWT login and refresh endpoints.
- Self-service password change with old-password verification and Django password validation.
- Restaurant, menu, menu item, table, order, and order-item models and APIs.
- Restaurant-scoped querysets, serializer validation, and object permissions.
- Nested order-item creation and updates with automatic price calculation.
- Order workflow rules for pending, preparing, ready, served, and cancelled states.
- Filtering, searching, ordering, and limit/offset pagination.
- Swagger/OpenAPI descriptions and schema validation.
- Docker development services for Django and MySQL.
- MySQL health check, automatic migrations, and persistent database volume.
- Environment-based Django and database configuration.
- Non-root Django container, localhost-only development ports, and Docker build exclusions for secrets.
- Automated model, serializer, permission, and end-to-end API tests.

## Verification

- 30 automated tests passing.
- Django system and deployment checks passing with production security flags.
- Swagger schema validation passing.
- Docker Compose configuration and MySQL health check passing.
- Real `.env` ignored by Git and excluded from Docker images.

## Main Development Commands

Start the project:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

Run all tests:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T web python manage.py test
```

Stop the project without deleting database data:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
```

Swagger is available at `http://127.0.0.1:8000/api/docs/`.

## Remaining Work

1. Add API throttling, with stricter limits for authentication endpoints.
2. Add production settings and `docker-compose.prod.yml`.
3. Replace Django's development server with Gunicorn.
4. Add Nginx and HTTPS configuration.
5. Add production logging, monitoring, and deployment automation.
6. Add caching only after measuring endpoints that benefit from it.
