# SocialAPI

A RESTful API for a microblogging platform built with FastAPI. Supports user authentication, posts, comments, and likes.

## Tech Stack

- **FastAPI** — web framework
- **PostgreSQL** — database
- **SQLAlchemy** — ORM
- **Alembic** — database migrations
- **JWT** — authentication
- **Docker** — containerization
- **GitHub Actions** — CI/CD

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Run with Docker

1. Clone the repository
```bash
   git clone https://github.com/TryDreem/socialapi.git
   cd socialapi
```

2. Create `.env` file in the root directory
```
   ENV_STATE=dev
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql+asyncpg://username:1234@postgres:5432/socialapi
   MAILGUN_API_KEY=your-mailgun-api-key
   MAILGUN_DOMAIN=your-mailgun-domain
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
```

3. Start the application
```bash
   docker-compose up --build
```

4. Open API docs at `http://localhost:8000/docs`

> **Note:** Email confirmation requires Mailgun credentials.
> If you don't have them, you can confirm email manually via SQL:
> ```bash
> docker exec -it socialapi_db psql -U username -d socialapi
> UPDATE users SET is_confirmed = true WHERE email = 'your@email.com';
> 
> Replace `username` with `POSTGRES_USER` value from your `docker-compose.yml`
> ```

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get access token |
| GET | `/auth/confirm` | Confirm email |
| GET | `/auth/me` | Get current user info |

### Posts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/post` | Create a post |
| GET | `/post` | Get all posts (paginated) |
| GET | `/post/{id}` | Get post by id |
| DELETE | `/post/{id}` | Delete a post |

### Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/post/{id}/comments` | Create a comment |
| GET | `/post/{id}/comments` | Get all comments (paginated) |
| DELETE | `/post/{id}/comments/{comment_id}` | Delete a comment |

### Likes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/post/{id}/like` | Like a post |
| DELETE | `/post/{id}/like` | Unlike a post |
| GET | `/post/{id}/like` | Get likes count |

## Running Tests
```bash
pytest tests/ -v
```