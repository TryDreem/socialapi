# SocialAPI

A production-ready RESTful API for a microblogging platform built with **FastAPI** and modern async Python stack.

> Live demo: [https://socialapi-wbc3.onrender.com/docs](https://socialapi-wbc3.onrender.com/docs)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI (async) |
| Database | PostgreSQL + SQLAlchemy (async ORM) |
| Migrations | Alembic |
| Caching | Redis |
| Auth | JWT (access + refresh tokens) |
| Background Tasks | Celery + Redis broker |
| Email | Mailgun API |
| Containerization | Docker + Docker Compose |
| Reverse Proxy | Nginx |
| CI/CD | GitHub Actions |

---

## Architecture

```
Client
  │
  ▼
Nginx (reverse proxy, port 80)
  │
  ▼
FastAPI (uvicorn, port 8000)
  │
  ├──► PostgreSQL (persistent data)
  │
  ├──► Redis (caching + refresh tokens)
  │
  └──► Celery Worker ──► Mailgun (email delivery)
```

### Key architectural decisions

**Async throughout** — FastAPI + asyncpg + SQLAlchemy async engine. Every database call is non-blocking, allowing high concurrency without thread overhead.

**Redis dual-purpose** — used both for response caching (posts, feed, search) with 5-minute TTL and for refresh token storage with 7-day TTL. Cache invalidation is pattern-based (`cache:posts:*`) on any write operation.

**JWT with refresh tokens** — short-lived access tokens (30 min) stored client-side, long-lived refresh tokens (7 days) stored in Redis. Logout invalidates the refresh token server-side.

**Celery for email** — confirmation emails are dispatched as background tasks via Celery so the registration endpoint returns immediately without waiting for the Mailgun API.

**Service layer** — business logic is separated from HTTP routing (but partially). Routers handle request/response, services handle data access and caching logic.

---

## Database Schema

```
users
  │
  ├──< posts (user_id → users.id)
  │     └──< likes   (post_id → posts.id, user_id → users.id)
  │     └──< comments (post_id → posts.id, user_id → users.id)
  │
  └──< follows (follower_id → users.id, following_id → users.id)
```

### Tables

- **users** — email, hashed password, email confirmation status
- **posts** — body (max 500 chars), author reference, timestamps
- **likes** — unique constraint on (user_id, post_id) prevents duplicate likes
- **comments** — body (max 500 chars), references to post and author
- **follows** — composite primary key (follower_id, following_id), self-referential on users

---

## API Endpoints

### Auth
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | ❌ | Register new user |
| POST | `/auth/login` | ❌ | Login, returns token pair |
| GET | `/auth/confirm` | ❌ | Confirm email via token |
| GET | `/auth/me` | ✅ | Get current user info |
| POST | `/auth/refresh` | ❌ | Refresh access token |
| POST | `/auth/logout` | ✅ | Invalidate refresh token |

### Posts
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/post` | ✅ | Create post |
| GET | `/post` | ❌ | Get all posts (paginated, sortable) |
| GET | `/post/search` | ❌ | Search posts by body |
| GET | `/post/{id}` | ❌ | Get post by id |
| PATCH | `/post/{id}` | ✅ | Update post |
| DELETE | `/post/{id}` | ✅ | Delete post |

### Comments
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/post/{id}/comments` | ✅ | Create comment |
| GET | `/post/{id}/comments` | ❌ | Get comments (paginated) |
| DELETE | `/post/{id}/comments/{comment_id}` | ✅ | Delete comment |

### Likes
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/post/{id}/like` | ✅ | Like a post |
| DELETE | `/post/{id}/like` | ✅ | Unlike a post |
| GET | `/post/{id}/like` | ❌ | Get likes count |

### Follows & Feed
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/users/{id}/follow` | ✅ | Follow user |
| DELETE | `/users/{id}/follow` | ✅ | Unfollow user |
| GET | `/users/{id}/followers` | ❌ | Get followers list |
| GET | `/feed` | ✅ | Get feed from followed users |

---

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Run with Docker

```bash
# 1. Clone the repository
git clone https://github.com/TryDreem/socialapi.git
cd socialapi

# 2. Create .env file
cp .env.example .env
# Edit .env with your values

# 3. Start all services
docker-compose up --build

# 4. Open API docs
# http://localhost/docs
```

### Environment variables

```env
ENV_STATE=dev
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql+asyncpg://username:password@postgres:5432/socialapi
REDIS_URL=redis://redis:6379
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=your-mailgun-domain
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> **Note:** Email confirmation requires Mailgun credentials.
> Without them, use the dev endpoint to confirm emails manually:
> ```
> POST /auth/confirm-dev/{email}
> ```

### Run tests

```bash
pytest tests/ -v
```

---

## Features

- **Async API** — fully async stack with FastAPI + asyncpg
- **JWT Authentication** — access/refresh token pair with Redis-backed invalidation
- **Redis Caching** — posts, feed, and search results cached with automatic invalidation
- **Follow System** — follow/unfollow users, personalized feed
- **Post Search** — case-insensitive full-text search with sorting and pagination
- **Rate Limiting** — per-endpoint rate limits via SlowAPI
- **Background Email** — async email delivery via Celery + Mailgun
- **Pagination** — all list endpoints support page/page_size parameters
- **Sorting** — posts sortable by newest, oldest, most liked

---

## Load Testing

Results with k6 (100 VUs, 2.5 minutes):

| Metric | Result |
|--------|--------|
| Requests/sec | 1054 |
| Avg response time | 46ms |
| Failed requests | 0% |