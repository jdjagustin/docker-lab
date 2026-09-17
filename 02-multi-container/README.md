# Stage 2 — multi-container with docker-compose

## What's here

A small task-list API (FastAPI) backed by a real PostgreSQL database,
wired together with `docker-compose.yml` instead of manual `docker run`
commands.

- `app/main.py` — the API: list tasks, create a task, mark one done.
- `app/Dockerfile` — same idea as stage 1, one image for the `web` service.
- `docker-compose.yml` — defines both services and how they connect.

## docker-compose.yml, section by section

```yaml
services:
  web:
    build: ./app                 # build this service's image from ./app/Dockerfile
    ports:
      - "8000:8000"               # host:container port mapping
    environment:
      DATABASE_URL: postgresql://taskuser:taskpass@db:5432/tasksdb
    depends_on:
      db:
        condition: service_healthy   # wait for db's healthcheck before starting web

  db:
    image: postgres:16            # use the official image directly, no Dockerfile needed
    environment:                  # postgres reads these on first boot to create the DB/user
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: taskpass
      POSTGRES_DB: tasksdb
    volumes:
      - db_data:/var/lib/postgresql/data   # persist data outside the container's lifecycle
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskuser -d tasksdb"]

volumes:
  db_data:                        # named volume, managed by Docker
```

Two things worth noticing:

1. **`db:5432` in `DATABASE_URL`** — `db` is not a hostname on your machine,
   it's the *service name*. Compose creates a private network where each
   service can reach the others by name. This only works between
   containers on that network, never from your host machine directly.
2. **The named volume** — without it, everything Postgres writes lives
   inside the container's own filesystem, gone the moment you
   `docker compose down -v` or remove the container. The volume survives
   independently of the container.

## Run it

```bash
docker compose up --build
```

Then, in another terminal:

```bash
curl -X POST localhost:8000/tasks -H "Content-Type: application/json" -d '{"title": "Study Docker"}'
curl localhost:8000/tasks
curl -X PATCH localhost:8000/tasks/1/done
```

Or open `http://localhost:8000/docs` for FastAPI's interactive Swagger UI —
you can try every endpoint from the browser.

```bash
docker compose down       # stop everything, keep the volume (data survives)
docker compose down -v    # stop everything AND delete the volume (data gone)
```

## Why `wait_for_db()` exists

Compose's `depends_on: condition: service_healthy` waits for Postgres'
*healthcheck* to pass, but there's a small window right after where the app
can still connect before Postgres is fully ready to serve. `wait_for_db()`
retries a few times instead of crashing on the first attempt — a pattern
you'll see in most real multi-container apps.
