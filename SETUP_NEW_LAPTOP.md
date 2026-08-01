# New Laptop Setup

## Install These Programs

Install these first:

- Python 3.12 or 3.13
- Git
- MySQL Server
- MySQL Workbench, optional
- VS Code

Check installs:

```bash
py --version
git --version
mysql --version
```

## Project Setup

Go to the project folder that contains `manage.py`:

```bash
cd resturantorderingapi
```

Create virtual environment:

```bash
py -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

Install Python packages:

```bash
py -m pip install -r requirements-minimal.txt
```

If `mysqlclient` fails on Windows, install this instead:

```bash
py -m pip install pymysql
```

Then add this to `resturantorderingapi/__init__.py` only if using `pymysql`:

```python
import pymysql

pymysql.install_as_MySQLdb()
```

## Environment File

Create `.env` beside `manage.py`:

```env
DB_NAME=restaurant_ordering_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

Do not upload `.env` to GitHub.

## MySQL Database

Open MySQL and run:

```sql
CREATE DATABASE restaurant_ordering_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Django Commands

Apply migrations:

```bash
py manage.py migrate
```

Create admin user:

```bash
py manage.py createsuperuser
```

Check project:

```bash
py manage.py check
```

Run server:

```bash
py manage.py runserver 127.0.0.1:8080
```

Open Swagger:

```text
http://127.0.0.1:8080/api/docs/
```

## Current Important Endpoints

JWT:

```text
POST /api/token/
POST /api/token/refresh/
```

Swagger:

```text
GET /api/schema/
GET /api/docs/
```

Users:

```text
GET     /api/users/
POST    /api/users/
GET     /api/users/<id>/
PUT     /api/users/<id>/
PATCH   /api/users/<id>/
DELETE  /api/users/<id>/
```

## Notes

- Use `py`, not `python`, for commands.
- Recreate `venv`; do not copy it from the old laptop.
- Recreate `.env`; it should not be in Git.
- MySQL database data is separate from project code.
- If port `8000` or `8001` is busy, use `8080`.
