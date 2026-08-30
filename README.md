# RestoHub Restaurant Ordering API

RestoHub is a backend API for managing restaurant operations from one place. It is built for restaurants that need to manage staff, menus, tables, and orders with clear role-based access.

The system supports multiple restaurants, so platform administrators can manage the whole application while restaurant owners and employees work only within the restaurants they belong to.

## What The API Covers

- User authentication with JWT
- Role-based access for platform admins, owners, waiters, and chefs
- Restaurant management
- Staff management
- Menu and menu item management
- Table management
- Order and order item management
- Order status updates
- Restaurant-scoped permissions
- Filtering, searching, ordering, and pagination
- Swagger/OpenAPI documentation

## Tech Stack

- Python
- Django
- Django REST Framework
- MySQL
- Simple JWT
- django-filter
- drf-spectacular
- Docker
- Docker Compose
- Gunicorn
- Nginx

## Project Structure

```text
resturantordering/
|-- resturantorderingapi/   # Django project settings and root URLs
|-- user/                   # Custom user model, auth, roles, and staff APIs
|-- restaurant/             # Restaurant APIs and permissions
|-- menu/                   # Menu APIs
|-- menuItem/               # Menu item APIs
|-- table/                  # Restaurant table APIs
|-- order/                  # Order and order item APIs
|-- nginx/                  # Nginx configuration
|-- Dockerfile
|-- docker-compose.yml
|-- docker-compose.dev.yml
|-- docker-compose.prod.yml
`-- requirements.txt
```

## Environment Variables

Create a local `.env` file from the example file:

```powershell
Copy-Item .env.example .env
```

The `.env` file is ignored by Git and should stay private. Use `.env.example` as the public template for required settings.

## Run Locally With Docker

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

Run migrations:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec web python manage.py migrate
```

Create an admin user:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

## API Documentation

After starting the project locally, open:

```text
http://127.0.0.1:8000/api/docs/
```

## Tests

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec web python manage.py test
```

## Notes

This repository contains the backend API only. Frontend clients can connect to the API using the documented endpoints and JWT authentication.

Private environment files, deployment notes, generated documents, and demo seed data are intentionally ignored from version control.
