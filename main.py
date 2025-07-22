import json
import threading
from fastapi import FastAPI, Response, status, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime
import os

app = FastAPI()

DATA_FILE = "books.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

lock = threading.Lock()
clients = set()


class Book(BaseModel):
    id: Optional[int] = None
    title: str
    author: str
    publication_year: int
    genre: str
    isbn: str

    @field_validator("title", "author", "genre", "isbn")
    @classmethod
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field must not be empty")
        return v



def read_books():
    with lock:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


def write_books(data):
    with lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)


async def notify_clients():
    data = read_books()
    disconnected = set()
    for ws in clients:
        try:
            await ws.send_json(data)
        except:
            disconnected.add(ws)
    for ws in disconnected:
        clients.remove(ws)



@app.post("/book")
async def create_or_update_book(book: Book, response: Response):

    if book.publication_year < 1450 or book.publication_year > datetime.now().year:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Publication year should be between 1450 and present year."}

    books = read_books()

    existing = next((b for b in books if b["isbn"] == book.isbn or
                     (b["title"] == book.title and b["author"] == book.author and b["publication_year"] == book.publication_year)), None)

    if existing:
        existing.update(book.dict(exclude_unset=True, exclude={"id"}))
        write_books(books)
        await notify_clients()
        return {"message": "Book updated", "book": existing}
    else:
        if any(b["isbn"] == book.isbn for b in books):
            raise HTTPException(status_code=400, detail="ISBN must be unique")
        new_id = max([b["id"] for b in books], default=0) + 1
        new_book = book.dict()
        new_book["id"] = new_id
        books.append(new_book)
        write_books(books)
        await notify_clients()
        return {"message": "Book created", "book": new_book}


@app.get("/books", response_model=List[Book])
def get_books(
    skip: int = 0,
    limit: int = 10,
    sort_by: Optional[str] = Query(None, enum=["title", "author", "publication_year"]),
    genre: Optional[str] = None,
    author: Optional[str] = None):
    books = read_books()

    if genre:
        books = [book for book in books if book["genre"].lower() == genre.lower()]
    if author:
        books = [book for book in books if book["author"].lower() == author.lower()]
    if sort_by:
        books.sort(key=lambda x: x[sort_by])
    return books[skip : skip + limit]


@app.delete("/book/{book_id}")
async def delete_book(book_id: int):
    books = read_books()
    book_to_delete = next((b for b in books if b["id"] == book_id), None)

    if not book_to_delete:
        raise HTTPException(status_code=404, detail="Book not found")

    books.remove(book_to_delete)
    write_books(books)
    await notify_clients()
    return {"message": "Book deleted", "book": book_to_delete}



@app.websocket("/ws/books")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        await notify_clients() 
        while True:
            await websocket.receive_text() 
    except WebSocketDisconnect:
        clients.remove(websocket)
