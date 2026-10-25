import os

import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, request

app = Flask(__name__)


def connect_db():
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"],
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        connect_timeout=5,
        row_factory=dict_row,
    )


@app.get("/health")
def health():
    return jsonify(status="healthy"), 200


@app.get("/ready")
def ready():
    try:
        with connect_db() as conn:
            conn.execute("SELECT 1 FROM public.tasks LIMIT 1")
        return jsonify(status="ready"), 200
    except psycopg.Error:
        return jsonify(status="database unavailable"), 503


@app.get("/api/tasks")
def list_tasks():
    with connect_db() as conn:
        tasks = conn.execute(
            "SELECT id, title, completed FROM public.tasks ORDER BY id DESC"
        ).fetchall()
    return jsonify(tasks)


@app.post("/api/tasks")
def add_task():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify(error="Expected a JSON object"), 400

    title = data.get("title")
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 200:
        return jsonify(error="Title must contain 1 to 200 characters"), 400

    with connect_db() as conn:
        task = conn.execute(
            """
            INSERT INTO public.tasks (title)
            VALUES (%s)
            RETURNING id, title, completed
            """,
            (title.strip(),),
        ).fetchone()
    return jsonify(task), 201


@app.post("/api/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    with connect_db() as conn:
        task = conn.execute(
            """
            UPDATE public.tasks SET completed = NOT completed
            WHERE id = %s
            RETURNING id, title, completed
            """,
            (task_id,),
        ).fetchone()
    if task is None:
        return jsonify(error="Task not found"), 404
    return jsonify(task)


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    with connect_db() as conn:
        task = conn.execute(
            "DELETE FROM public.tasks WHERE id = %s RETURNING id",
            (task_id,),
        ).fetchone()
    if task is None:
        return jsonify(error="Task not found"), 404
    return "", 204


@app.get("/")
def home():
    from flask import render_template
    return render_template("index.html")
