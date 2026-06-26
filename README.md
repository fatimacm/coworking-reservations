# Coworking Reservations API

REST API for managing coworking space reservations, built with FastAPI and PostgreSQL.

The project includes JWT authentication, reservation management, business rule validations, automated tests, Docker support, and deployment on Railway.

## Features

### Authentication
* User registration and login.
* Password hashing with bcrypt.
* JWT authentication using OAuth2.
* `/me` endpoint to retrieve the current user.

### Reservation Management
* Create reservations.
* View reservations.
* Update reservations.
* Cancel reservations using soft delete.

### Reservation Rules
* Reservations cannot be created in the past.
* Reservations must stay within business hours (08:00 - 20:00).
* Minimum reservation duration is 30 minutes.
* Maximum reservation duration is 8 hours.
* Users cannot exceed 8 reserved hours per day.
* Reservation overlaps are not allowed.
* Cancelled reservations do not count toward daily limits.

## Tech Stack
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* JWT Authentication
* Docker
* Pytest
* GitHub Actions
* Railway

## Project Structure
```text
coworking-reservations/
├── app/
├── tests/
├── alembic/
├── .github/workflows/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/fatimacm/coworking-reservations.git
cd coworking-reservations
```

### 2. Create environment variables
``` bash
cp .env.example .env
```

Example configuration:

``` bash
DATABASE_URL=postgresql://coworking_user:your_password@db:5432/coworking_db
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate a secret key:

``` bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Start containers

``` bash
docker-compose up --build
```

### 4. Run migrations

``` bash 
docker-compose exec api alembic upgrade head
```

The API will be available at: http://localhost:8000

## API Documentation
- Swagger UI → http://localhost:8000/docs

## Main Endpoints

### Authentication

| Method | Endpoint   | Description                              |
|--------|------------|------------------------------------------|
| POST   | /register  | Register a new user |
| POST   | /login     | Login and obtain JWT token              |
| GET    | /me        | Retrieve current user           |

### Reservations

| Method | Endpoint              | Description                          | 
|--------|-----------------------|--------------------------------------|
| GET    | /reservations         | List user reservations |
| POST   | /reservations         | Create reservation               |
| GET    | /reservations/{id}    | Retrieve reservation               |
| PUT    | /reservations/{id}    | Update reservation                   |
| DELETE | /reservations/{id}    | Cancel reservation     |

### Running Tests

Run all tests with:

``` bash
docker-compose exec api pytest -v
```

Tests cover:

* Authentication
* Reservation CRUD
* Access restrictions
* Reservation policies
* Business rules

### Deployment

The application is currently deployed on Railway and uses GitHub Actions for automated test execution.

## Author
Fatima Coronado
- GitHub: @fatimacm