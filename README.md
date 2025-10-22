# Coworking Reservations API

A RESTful API for managing coworking space reservations, built with FastAPI, PostgreSQL, and JWT authentication. Containerized with Docker Compose for reproducible local development and testing.

## 🚀 Features

### User Authentication
- User registration and login with email and password
- Secure password hashing with bcrypt
- Token-based authentication using OAuth2 + JWT
- `/me` endpoint to retrieve current user information

### Reservation Management
- Create, view, update, and cancel reservations
- Users can only manage their own reservations
- Soft deletion for preserving data integrity

## 📋 Requirements

- Python 3.11+
- Docker & Docker Compose
- Git

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/fatimacm/coworking-reservations.git
cd coworking-reservations
```

### 2. Create environment variables
``` bash
cp .env.example .env
```

Edit .env:

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

### 3. Start the project

``` bash
docker-compose up --build
```

### 4. Run database migrations

``` bash 
docker-compose exec api alembic upgrade head
```

The API will be available at: http://localhost:8000

## 📚 API Documentation
- Swagger UI → http://localhost:8000/docs
- ReDoc → http://localhost:8000/redoc

## 🔑 Endpoints Overview

### Authentication

| Method | Endpoint   | Description                              |
|--------|------------|------------------------------------------|
| POST   | /register  | Create new user (username, email, password) |
| POST   | /login     | Login and receive JWT token              |
| GET    | /me        | Get current authenticated user           |

### Reservations

| Method | Endpoint              | Description                          | 
|--------|-----------------------|--------------------------------------|
| GET    | /reservations         | Get all reservations for current user |
| POST   | /reservations         | Create new reservation               |
| GET    | /reservations/{id}    | Retrieve a reservation               |
| PUT    | /reservations/{id}    | Update reservation                   |
| DELETE | /reservations/{id}    | Cancel reservation (soft delete)     |

### 🧪 Running Tests
Run all tests with:

``` bash
docker-compose exec api pytest -v
```

Pytest will automatically use the test configuration defined in conftest.py


### 📁 Project Structure

```
coworking-reservations/
├── app/ # FastAPI application code
├── tests/ # Test suites
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md

```
## Author
Fatima Coronado
- GitHub: @fatimacm