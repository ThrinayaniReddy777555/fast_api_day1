from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Todo App", description="A simple Todo API using FastAPI", version="1.0.0")

# Temporary in-memory storage
todos = {}
counter = 1  # auto-increment ID


# ── Models ──────────────────────────────────────────────────────────────────

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Welcome to the Todo API! Visit /docs to explore."}


@app.get("/todos")
def get_all_todos():
    """Get all todos"""
    return {"todos": list(todos.values()), "total": len(todos)}


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    """Get a single todo by ID"""
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return todos[todo_id]


@app.post("/todos", status_code=201)
def create_todo(todo: TodoCreate):
    """Create a new todo"""
    global counter
    new_todo = {
        "id": counter,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed
    }
    todos[counter] = new_todo
    counter += 1
    return new_todo


@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate):
    """Update an existing todo"""
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    
    existing = todos[todo_id]
    if todo.title is not None:
        existing["title"] = todo.title
    if todo.description is not None:
        existing["description"] = todo.description
    if todo.completed is not None:
        existing["completed"] = todo.completed

    todos[todo_id] = existing
    return existing


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    """Delete a todo by ID"""
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    deleted = todos.pop(todo_id)
    return {"message": f"Todo '{deleted['title']}' deleted successfully"}


@app.delete("/todos")
def delete_all_todos():
    """Delete all todos"""
    todos.clear()
    return {"message": "All todos deleted successfully"}
