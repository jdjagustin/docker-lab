import os
import time

import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DATABASE_URL = os.environ["DATABASE_URL"]

app = FastAPI(title="Docker Lab - Task API")


class TaskIn(BaseModel):
    title: str


class Task(BaseModel):
    id: int
    title: str
    done: bool


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def wait_for_db(retries: int = 10, delay: float = 2.0):
    """The db container can take a few seconds to accept connections even
    after its healthcheck passes for compose. Retry instead of crashing."""
    last_error = None
    for _ in range(retries):
        try:
            conn = get_conn()
            conn.close()
            return
        except psycopg2.OperationalError as exc:
            last_error = exc
            time.sleep(delay)
    raise RuntimeError(f"Database not reachable: {last_error}")


def init_db():
    wait_for_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                );
                """
            )
        conn.commit()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/tasks", response_model=list[Task])
def list_tasks():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks ORDER BY id;")
            rows = cur.fetchall()
    return [{"id": r[0], "title": r[1], "done": r[2]} for r in rows]


@app.post("/tasks", response_model=Task)
def create_task(task: TaskIn):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done;",
                (task.title,),
            )
            row = cur.fetchone()
        conn.commit()
    return {"id": row[0], "title": row[1], "done": row[2]}


@app.patch("/tasks/{task_id}/done", response_model=Task)
def mark_done(task_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET done = TRUE WHERE id = %s RETURNING id, title, done;",
                (task_id,),
            )
            row = cur.fetchone()
        conn.commit()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": row[0], "title": row[1], "done": row[2]}


@app.get("/health")
def health():
    return {"status": "ok"}
