# Phase II: Database Migrations, User Modeling, and Authentication Setup

## Overview

In Phase II of the DocuSense backend development, we bridged the gap between our FastAPI web application and our PostgreSQL database. This phase established the database schema, configured automated migration pipelines, implemented strict API data validation, and laid down the core security infrastructure for user authentication.

---

## Deep Dive: Tools, Techniques, and Architectures

### 1. Alembic and Database Migrations

Alembic is the lightweight database migration tool for SQLAlchemy. It acts as a version control system for our database schema, allowing us to evolve our database structure over time without losing existing data.

#### How `--autogenerate` Works

When we run:

```bash
alembic revision --autogenerate -m "create_users_table"
```

Alembic does not guess what we want. Instead, it performs a real-time comparison:

1. It inspects our local PostgreSQL database schema to see what tables and columns currently exist.
2. It looks at the `Base.metadata` in our Python code (where all SQLAlchemy models like `User` are registered).
3. It calculates the difference (diff) between the two.
4. It automatically writes the Python code necessary to bring the database in line with our models, generating a migration script inside `alembic/versions/`.

#### How `upgrade head` Works

When we run:

```bash
alembic upgrade head
```

- `head` refers to the latest (most recent) migration script in our versions folder.
- Alembic looks at a special table in our database called `alembic_version`. This table stores exactly one value: the revision ID of the last migration that was successfully applied.
- If the database is empty, it runs all migration scripts in chronological order up to the latest one (`head`).
- If our database is already on version A, and the latest version is C, Alembic is smart enough to only run the steps to transition from A to B to C.

---

### 2. Dependency Injection via `Depends(get_db)`

In FastAPI, Dependency Injection is a software design pattern where an object (the route handler) receives other helper objects it needs (the database session) from an external source, rather than creating them internally.

#### The `get_db` Async Generator

We define our database session generator like this:

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
```

#### The Lifecycle of a Request

When a route uses `db: AsyncSession = Depends(get_db)`:

1. **Request Arrives** — FastAPI intercepts the request and runs `get_db()`.
2. **Session Opened** — An asynchronous database session (`session`) is opened.
3. **Control Handed Over** — The `yield` statement pauses the generator and hands the active database session directly to our route function.
4. **Endpoint Executes** — Our route function executes database queries (e.g., saving a user).
5. **Clean Up** — Once the route returns its response (or throws an error), control goes back to `get_db()`. The `async with` block automatically exits, closing the database connection and returning it to the connection pool. This prevents memory leaks and stale database connections.

---

### 3. OAuth2 Architecture and Security Tools

To protect our API, we implement the industry-standard OAuth2 protocol. FastAPI provides native, low-level security tools that make integration simple.

#### `OAuth2PasswordBearer`

This utility tells FastAPI that the application uses OAuth2 "Password Flow" (logging in with a username/email and password to receive a bearer token).

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
```

- **Automatic Header Extraction** — When we inject `token: str = Depends(oauth2_scheme)` into a protected route, FastAPI automatically looks for an `Authorization` header in the incoming request containing `Bearer <your_token>`. If the header is missing or formatted incorrectly, it automatically throws an HTTP 401 Unauthorized exception before our code even runs.
- **Swagger UI Integration** — The `tokenUrl` parameter tells our automatic Swagger documentation (`/docs`) where to send user credentials when they click the "Authorize" padlock button.

#### `OAuth2PasswordRequestForm`

This is a built-in dependency that FastAPI uses to parse incoming login credentials.

```python
@router.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    ...
```

- OAuth2 specifications mandate that login credentials must be sent as Form Data (`multipart/form-data` or `application/x-www-form-urlencoded`), not as raw JSON.
- `OAuth2PasswordRequestForm` parses this form data and exposes it via `form_data.username` and `form_data.password`.
- **Note:** Even though our application uses email to log in, we still read it using `form_data.username` because the OAuth2 standard uses the term "username" generically for whatever unique identifier the user logs in with.

---

### 4. Modern Password Security (Direct bcrypt)

In modern backend engineering, storing plain-text passwords is a critical vulnerability. Instead, we convert passwords into irreversible cryptographic strings called hashes.

#### Why We Choose Direct bcrypt over passlib

Historically, Python developers used `passlib` to handle hashing. However, we opted to use the core `bcrypt` package directly due to shifts in the Python landscape:

- **Unmaintained Dependency** — `passlib` has not been updated since October 2020. It relies internally on Python's legacy `crypt` module, which was officially removed in Python 3.13. Using `passlib` creates immediate technical debt and breaks on modern runtimes.
- **Compatibility Errors** — Modern versions of the `bcrypt` library throw errors when wrapped by older versions of `passlib`.
- **Clean Code** — Using `bcrypt` directly allows us to write highly explicit, future-proof utility functions without unnecessary middleware overhead:

```python
import bcrypt

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')
```

- **Salt (`bcrypt.gensalt()`)** — Generates a unique, random string appended to the password before hashing. This ensures that if two users have the exact same password, their stored hashes are completely different, preventing rainbow table database attacks.

---

### 5. Pydantic vs. SQLAlchemy Dual-Model Pattern

A core architectural pattern in FastAPI is the strict separation between database entities and data transfer objects (DTOs).

| Feature | SQLAlchemy Models (`app/models/`) | Pydantic Schemas (`app/schemas/`) |
|---|---|---|
| Purpose | Storage Contract: Defines database tables, relationships, and data persistence constraints. | Communication Contract: Defines data validation for API inputs and serialization for API outputs. |
| Example | `User` class mapping to the `users` table. | `UserCreate` validating request bodies; `UserResponse` formatting output. |
| Scope | Speaks directly to PostgreSQL. | Speaks directly to HTTP clients (browsers, mobile apps). |

#### Enforcing the Boundary

By separating these two, we gain powerful security control:

- **`UserCreate`** — Enforces strict input validation rules (e.g., validating that an email is structurally correct via `EmailStr`, and enforcing a minimum password length of 8 characters).
- **`UserResponse`** — Ensures that when we return a user object to the frontend, we never expose the hashed password. We only serialize public fields like the user's `id` and `email`.
- **`from_attributes = True`** (formerly `orm_mode`) — This Pydantic configuration tells Pydantic that it is allowed to read fields directly from a lazy-loaded database object (like `user_db_instance.email`) instead of requiring a native Python dictionary.

---

## Key Learnings and Takeaways

- **Docker Port Networking (HOST:CONTAINER)** — We learned that mapping Docker ports follows a strict routing structure. If we change ports to resolve conflicts (e.g., using `5431:5432` because our host OS is already running local Postgres on `5432`), the left side (`5431`) is where our host machine makes connections, while the right side (`5432`) must remain unchanged because Postgres inside the isolated container is hardcoded to listen internally on `5432`.
- **Route-First Development Flow** — Writing route signatures first provides immediate clarity. By laying down `/register` and `/login` endpoints, we instantly know exactly what Pydantic schemas must be built to validate inputs and what queries are required to communicate with PostgreSQL.
- **Dependency Lifecycles** — FastAPI's dependency system is exceptionally powerful. It simplifies resource management by abstracting away the setup and teardown steps of crucial systems like database engines and security decoders.
