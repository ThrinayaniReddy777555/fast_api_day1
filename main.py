"""
Todo API - FastAPI Application
================================
A simple RESTful Todo API built with FastAPI and Pydantic.

Features:
    - Create, read, update, and delete (CRUD) todo items
    - In-memory storage with auto-incrementing IDs
    - Input validation via Pydantic models
    - Interactive API docs at /docs (Swagger UI) and /redoc (ReDoc)

Usage:
    Run with:
        uvicorn main:app --reload

    Then visit:
        http://127.0.0.1:8000/docs  → Swagger UI
        http://127.0.0.1:8000/redoc → ReDoc

Author: Thrinayani
Version: 1.0.0
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional


# ── App Initialization ────────────────────────────────────────────────────────

app = FastAPI(
    title="Todo App",
    description=(
        "A simple **Todo API** built with FastAPI.\n\n"
        "Supports full **CRUD** operations:\n"
        "- ✅ **Create** a new todo\n"
        "- 📋 **Read** one or all todos\n"
        "- ✏️ **Update** an existing todo\n"
        "- 🗑️ **Delete** one or all todos\n\n"
        "> **Note:** Data is stored in memory and resets on server restart."
    ),
    version="1.0.0",
    contact={
        "name": "Thrinayani",
    },
    license_info={
        "name": "MIT",
    },
)

# ── In-memory storage ─────────────────────────────────────────────────────────

# Stores todos as {id: todo_dict}
todos: dict = {}

# Auto-incrementing ID counter
counter: int = 1


# ── Pydantic Models ───────────────────────────────────────────────────────────

class TodoCreate(BaseModel):
    """
    Request body schema for creating a new todo item.

    Attributes:
        title (str): The title/name of the todo task. Required.
        description (Optional[str]): An optional longer description of the task.
        completed (bool): Whether the task is already done. Defaults to False.

    Example:
        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": false
        }
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="The title of the todo item.",
        examples=["Buy groceries"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="An optional description with more details about the task.",
        examples=["Milk, eggs, bread"],
    )
    completed: bool = Field(
        default=False,
        description="Whether the todo item has been completed.",
        examples=[False],
    )


class TodoUpdate(BaseModel):
    """
    Request body schema for partially updating an existing todo item.

    All fields are optional — only the fields provided will be updated
    (partial/PATCH-style update via PUT endpoint).

    Attributes:
        title (Optional[str]): New title to set on the todo.
        description (Optional[str]): New description to set.
        completed (Optional[bool]): New completion status.

    Example:
        {
            "completed": true
        }
    """

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="New title for the todo item (leave blank to keep existing).",
        examples=["Buy groceries and cook dinner"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="New description for the todo (leave blank to keep existing).",
        examples=["Also get some vegetables"],
    )
    completed: Optional[bool] = Field(
        default=None,
        description="New completion status (leave blank to keep existing).",
        examples=[True],
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get(
    "/",
    summary="Root",
    description="Health-check / welcome endpoint. Confirms the API is running.",
    tags=["General"],
)
def root():
    """
    Return a welcome message.

    Returns:
        dict: A JSON object with a welcome message and a hint to visit /docs.

    Example Response:
        {
            "message": "Welcome to the Todo API! Visit /docs to explore."
        }
    """
    return {"message": "Welcome to the Todo API! Visit /docs to explore."}


@app.get(
    "/todos",
    summary="Get All Todos",
    description="Retrieve every todo item currently stored in memory.",
    tags=["Todos"],
)
def get_all_todos():
    """
    Fetch all todos.

    Returns:
        dict: A JSON object containing:
            - **todos** (list): All todo items.
            - **total** (int): Total count of todos.

    Example Response:
        {
            "todos": [
                {"id": 1, "title": "Buy groceries", "description": "Milk, eggs", "completed": false}
            ],
            "total": 1
        }
    """
    return {"todos": list(todos.values()), "total": len(todos)}


@app.get(
    "/todos/{todo_id}",
    summary="Get Todo by ID",
    description="Retrieve a single todo item using its unique integer ID.",
    tags=["Todos"],
)
def get_todo(todo_id: int):
    """
    Fetch a specific todo by its ID.

    Args:
        todo_id (int): The unique identifier of the todo item (path parameter).

    Returns:
        dict: The todo item matching the given ID.

    Raises:
        HTTPException (404): If no todo with the given ID exists.

    Example Response (200):
        {
            "id": 1,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": false
        }

    Example Response (404):
        {
            "detail": "Todo with id 99 not found"
        }
    """
    if todo_id not in todos:
        raise HTTPException(
            status_code=404,
            detail=f"Todo with id {todo_id} not found",
        )
    return todos[todo_id]


@app.post(
    "/todos",
    status_code=201,
    summary="Create a Todo",
    description="Create a new todo item. Returns the created todo with its assigned ID.",
    tags=["Todos"],
)
def create_todo(todo: TodoCreate):
    """
    Create a new todo item.

    The server auto-assigns a unique integer ID to each new todo.

    Args:
        todo (TodoCreate): The request body with todo details.

    Returns:
        dict: The newly created todo including its server-assigned ID.

    Example Request Body:
        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": false
        }

    Example Response (201):
        {
            "id": 1,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": false
        }
    """
    global counter
    new_todo = {
        "id": counter,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
    }
    todos[counter] = new_todo
    counter += 1
    return new_todo


@app.put(
    "/todos/{todo_id}",
    summary="Update a Todo",
    description=(
        "Partially update an existing todo item. "
        "Only the fields included in the request body will be changed — "
        "omitted fields retain their current values."
    ),
    tags=["Todos"],
)
def update_todo(todo_id: int, todo: TodoUpdate):
    """
    Partially update a todo by ID.

    Only the fields explicitly passed in the request body are updated.
    This behaves like a PATCH despite using the PUT HTTP method.

    Args:
        todo_id (int): The ID of the todo to update (path parameter).
        todo (TodoUpdate): The request body with fields to update.

    Returns:
        dict: The updated todo item.

    Raises:
        HTTPException (404): If no todo with the given ID exists.

    Example Request Body (mark as completed):
        {
            "completed": true
        }

    Example Response (200):
        {
            "id": 1,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": true
        }
    """
    if todo_id not in todos:
        raise HTTPException(
            status_code=404,
            detail=f"Todo with id {todo_id} not found",
        )

    existing = todos[todo_id]
    if todo.title is not None:
        existing["title"] = todo.title
    if todo.description is not None:
        existing["description"] = todo.description
    if todo.completed is not None:
        existing["completed"] = todo.completed

    todos[todo_id] = existing
    return existing


@app.delete(
    "/todos/{todo_id}",
    summary="Delete a Todo",
    description="Permanently delete a single todo item by its ID.",
    tags=["Todos"],
)
def delete_todo(todo_id: int):
    """
    Delete a specific todo by ID.

    Args:
        todo_id (int): The ID of the todo to delete (path parameter).

    Returns:
        dict: A confirmation message with the title of the deleted todo.

    Raises:
        HTTPException (404): If no todo with the given ID exists.

    Example Response (200):
        {
            "message": "Todo 'Buy groceries' deleted successfully"
        }

    Example Response (404):
        {
            "detail": "Todo with id 99 not found"
        }
    """
    if todo_id not in todos:
        raise HTTPException(
            status_code=404,
            detail=f"Todo with id {todo_id} not found",
        )
    deleted = todos.pop(todo_id)
    return {"message": f"Todo '{deleted['title']}' deleted successfully"}


@app.delete(
    "/todos",
    summary="Delete All Todos",
    description="Wipe all todo items from memory. This action cannot be undone.",
    tags=["Todos"],
)
def delete_all_todos():
    """
    Delete every todo item in storage.

    Clears the entire in-memory todos dictionary.

    Returns:
        dict: A confirmation message indicating all todos were removed.

    Example Response (200):
        {
            "message": "All todos deleted successfully"
        }
    """
    todos.clear()
    return {"message": "All todos deleted successfully"}
