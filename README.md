# Docker Lab

A hands-on Docker lab for beginners. You build and run two small, real apps
and along the way you cover the fundamentals: images, containers, Dockerfile
instructions, port mapping, docker-compose, environment variables, networking
between containers, and named volumes.

No prior Docker experience assumed — every stage has its own README that
explains each line of the files, not just the commands to copy-paste.

## Prerequisites

- Docker Desktop (or Docker Engine + the Compose plugin) installed and running
- A terminal
- (Nice to have) `curl` or a REST client to poke at the running API

Check you're ready:

```
docker --version
docker compose version
```

## Structure

| Folder | What it teaches |
|---|---|
| [`01-single-container/`](./01-single-container) | One app, one Dockerfile, one container. `docker build`, `docker run`, port mapping, image layers. |
| [`02-multi-container/`](./02-multi-container) | A FastAPI + PostgreSQL task API. `docker-compose`, service-to-service networking, env vars, named volumes, healthchecks. |

Go through them in order — stage 2 builds on concepts stage 1 introduces.

## Quick start

```bash
# Stage 1
cd 01-single-container
docker build -t docker-lab-hello .
docker run -p 5000:5000 docker-lab-hello
# visit http://localhost:5000

# Stage 2 (open a new terminal, or Ctrl+C the one above first)
cd ../02-multi-container
docker compose up --build
# visit http://localhost:8000/docs
```

## Troubleshooting

**"address already in use" when running stage 1 on port 5000** -- on macOS,
port 5000 is usually already taken by the AirPlay Receiver. It's not a bug
in this repo. Either map to a different host port:

```bash
docker run -p 5050:5000 docker-lab-hello
```

or free up 5000: System Settings -> General -> AirDrop & Handoff -> turn
off "AirPlay Receiver".

## Docker cheat sheet

| Command | What it does |
|---|---|
| `docker build -t name .` | Build an image from the Dockerfile in the current directory |
| `docker run -p host:container name` | Run a container from an image, mapping a port |
| `docker ps` / `docker ps -a` | List running / all containers |
| `docker logs <id>` | See a container's stdout/stderr |
| `docker exec -it <id> bash` | Open a shell inside a running container |
| `docker stop <id>` / `docker rm <id>` | Stop / remove a container |
| `docker compose up --build` | Build and start every service in `docker-compose.yml` |
| `docker compose down` | Stop and remove the services (keeps named volumes) |
| `docker compose down -v` | Same, but also deletes named volumes — data loss on purpose, for the exercise below |

## Exercises (try these once both stages run)

1. In stage 1, run two containers from the same image on two different host
   ports (`-p 5001:5000` and `-p 5002:5000`) and hit both — notice each
   reports a different `container_hostname`, proving they're isolated.
2. In stage 2, create a few tasks, then run `docker compose down -v` and
   bring it back up — the data is gone. Now do it again with plain
   `docker compose down` (no `-v`) — the data survives. That's what the
   named volume is for.
3. Rewrite stage 1's Dockerfile as a multi-stage build.
4. Add a Redis service to stage 2's `docker-compose.yml` and use it to
   cache the `GET /tasks` response.
5. Move the hard-coded DB credentials in `docker-compose.yml` into a
   `.env` file and reference them with `${VAR}` — this is how you'd avoid
   committing secrets in a real project.

## License

MIT
