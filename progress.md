# Restaurant Ordering API Progress

## Project Direction

This is a SaaS-style internal restaurant ordering backend.

The system is for restaurant staff:

- Platform admin manages the SaaS platform.
- Owner manages restaurant users/staff.
- Waiter creates table orders.
- Chef receives and updates kitchen orders.

No public customer ordering flow is planned right now.

## Setup Completed

- Django project created.
- `user` app created.
- MySQL database configured through `.env`.
- Database password removed from `settings.py`.
- Django REST Framework configured.
- Simple JWT configured.
- Swagger/OpenAPI configured with `drf-spectacular`.
- Custom user model configured with `AUTH_USER_MODEL = "user.User"`.
- User migrations exist.

## User Model

Custom user model is based on:

- `AbstractBaseUser`
- `PermissionsMixin`
- custom `UserManager`

Login field:

- `email`

Current user fields:

- `email`
- `first_name`
- `last_name`
- `is_active`
- `is_staff`
- `role`

Current roles:

- `platform_admin`
- `owner`
- `waiter`
- `chef`

## User Admin

Custom Django admin is configured for the custom user.

Admin supports:

- listing users
- searching by email/name/role
- ordering by email
- creating users with `password1` and `password2`
- editing role and permission fields

## User API

User serializer is configured.

It supports:

- creating users
- updating users
- hashing passwords correctly
- hiding password from responses
- requiring password on create
- allowing password to be optional on update
- preventing non-platform-admin users from assigning `platform_admin`

User API uses one DRF `ModelViewSet`:

- `UserViewSet`

Routes are wired through a DRF router.

Current user endpoints:

```text
GET     /api/users/
POST    /api/users/
GET     /api/users/<id>/
PUT     /api/users/<id>/
PATCH   /api/users/<id>/
DELETE  /api/users/<id>/
```

Permission behavior:

- Platform admin can access all users.
- Owner can access users with roles `owner`, `waiter`, and `chef`.
- Waiter and chef currently get no user queryset access.

## Auth And Docs Endpoints

JWT endpoints:

```text
POST /api/token/
POST /api/token/refresh/
```

Swagger/OpenAPI endpoints:

```text
GET /api/schema/
GET /api/docs/
```

## Important Notes

- Run Django commands with `py`, not `python`.
- If port `8000` or `8001` is blocked, use a higher port like:

```bash
py manage.py runserver 127.0.0.1:8080
```

- The project folder name is currently spelled `resturantorderingapi`.
- The app file is named `serializer.py`, not the more common `serializers.py`.

## Next Steps

1. Run:

```bash
py manage.py check
```

2. Confirm migrations are applied:

```bash
py manage.py migrate
```

3. Create a superuser/platform admin:

```bash
py manage.py createsuperuser
```

4. Test JWT login:

```text
POST /api/token/
```

5. Test user CRUD in Swagger:

```text
/api/docs/
```

6. After user app is verified, start the restaurant/tenant app.
