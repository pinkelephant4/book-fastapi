# 📚 FastAPI Book Manager

This is a FastAPI-based web application that provides CRUD operations for managing a collection of books stored in a JSON file. It also supports real-time updates via WebSocket.


## 🚀 Features

- 📖 **Create/Update** books in a single endpoint  
  - Creates a book if it doesn’t exist based on ISBN or (title, author, publication_year)
  - Updates an existing book if it already exists
  - Validates that ISBN is unique
  - Validates publication year is between 1450 and current year
- 🔍 **Read** all books with:
  - Pagination (`skip` and `limit`)
  - Sorting (`title`, `author`, or `publication_year`)
  - Filtering by `author` or `genre`
- ❌ **Delete** books by ID
- 🔁 **Real-time updates** using WebSocket when books are created, updated, or deleted
- 🧾 **Thread-safe** file read/write operations using `threading.Lock`


## 📁 Project Structure

```
.
├── main.py           # FastAPI application
├── books.json        # JSON data storage
├── requirements.txt  # Python dependencies
└── index.html    # WebSocket test HTML

````

## 🧪 Running the Application

### 1. 📦 Install dependencies

```bash
pip install -r requirements.txt
```

### 2. ▶️ Start the server

```bash
uvicorn main:app --reload
```

### 3. 🌐 Access the Web App and API

* Open `http://localhost:8000` for the WebSocket-enabled book viewer
* Open `http://localhost:8000/docs` for interactive API docs (Swagger UI)

## 📬 API Endpoints

### 1. Create or Update Book ➕ 

```
POST /book
```

**Request Body:**

```json
{
  "title": "1984",
  "author": "George Orwell",
  "publication_year": 1949,
  "genre": "Dystopian",
  "isbn": "9780451524935"
}
```


### 2. Get All Books 📚 

```
GET /books?skip=0&limit=10&sort_by=title&genre=Fiction&author=Orwell
```

Query params:

* `skip`: number of items to skip
* `limit`: max items to return
* `sort_by`: `title`, `author`, or `publication_year`
* `genre` and/or `author`: to filter results


### 3. Delete Book ❌ 

```
DELETE /book/{book_id}
```

Deletes book by `id`.


### 4. WebSocket for Live Updates 🔁 

```
ws://localhost:8000/ws
```

Clients receive the entire updated list of books whenever a change (create/update/delete) is made.


## ✅ Validation Rules

* All fields are required
* `title`, `author`, `genre` must be non-empty strings
* `isbn` must be unique across all books
* `publication_year` must be between 1450 and the current year


## 📂 Data Storage

All book data is stored in a local JSON file (`books.json`). No database is used. Access is synchronized with a thread lock for safety.

## 🧠 Future Improvements

* Add client-side UI for adding/editing books
* Add user authentication
* Export book data to CSV
