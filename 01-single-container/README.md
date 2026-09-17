# Stage 1 — one app, one container

## What's here

- `app.py` — a tiny Flask app with two routes: `/` and `/health`.
- `requirements.txt` — its one dependency (Flask).
- `Dockerfile` — the recipe Docker uses to turn this folder into an image.

## The Dockerfile, line by line

```dockerfile
FROM python:3.12-slim        # start from an existing image that already has Python
WORKDIR /app                 # every instruction below runs from /app inside the image
COPY requirements.txt .      # copy just this file first...
RUN pip install -r requirements.txt   # ...so this layer gets cached and skipped
                                        # on rebuilds unless requirements.txt changes
COPY app.py .                 # now copy the actual app code
EXPOSE 5000                   # documentation: "this app listens on 5000"
CMD ["python", "app.py"]      # the command that runs when a container starts
```

Docker images are built in layers, one per instruction, and cached layer by
layer. That's why `requirements.txt` is copied and installed *before* the
rest of the code — changing `app.py` shouldn't force a full `pip install`
again.

## Build and run

```bash
docker build -t docker-lab-hello .
docker run -p 5000:5000 docker-lab-hello
```

Visit `http://localhost:5000` — you should see a JSON message with a
`container_hostname`. That hostname is the container's own ID, not your
machine's — that's the container's isolated view of "who am I".

Useful while it's running, in another terminal:

```bash
docker ps                 # see the running container and its ID
docker logs <id>          # see what it printed
docker exec -it <id> sh   # get a shell inside it
docker stop <id>          # stop it
```

## Try it

Run two containers from the same image on two different host ports:

```bash
docker run -d -p 5001:5000 docker-lab-hello
docker run -d -p 5002:5000 docker-lab-hello
curl localhost:5001
curl localhost:5002
```

Same image, same code — but each reports a different `container_hostname`.
That's container isolation: two independent processes, each thinking it's
the only one running.
