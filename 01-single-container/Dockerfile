FROM python:3.12-slim

WORKDIR /app

# Copy just the dependency list first so Docker can cache this layer
# and skip re-installing packages when only app.py changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Documents the port the app listens on. Doesn't publish it by itself —
# that's what `-p` on `docker run` is for.
EXPOSE 5000

CMD ["python", "app.py"]
