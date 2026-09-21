# FastAPI URL Shortener API

A production-grade, RESTful URL shortener built with FastAPI and PostgreSQL. This project goes beyond basic CRUD operations by implementing secure stateless authentication, full resource lifecycle management, and strict timezone handling.

## 🚀 Core Features

* **Robust Authentication:** OAuth2 Password Flow utilizing JWTs (`HS256`) and native `bcrypt` password hashing with dynamic salting.


* **Server-Side Logout:** True token revocation using a PostgreSQL-backed blacklist, evaluated inside the dependency injection pipeline to reject invalidated tokens instantly.


* **Link Lifecycle Management:** Full support for custom shortcodes, click analytics, timed expiration (returning `410 Gone`), and ownership-scoped deletion.


* **Dynamic Properties:** Expiration status is calculated on the fly using Python `@property` decorators and serialized seamlessly via Pydantic V2 `from_attributes`.


* **Timezone Consistency:** Completely immune to server-local time drift by forcing offset-naive UTC storage at the database driver level, allowing the frontend to safely translate timestamps to local time.



## 🛠️ Tech Stack

* **Framework:** FastAPI


* **Database:** PostgreSQL


* **ORM:** SQLAlchemy


* **Serialization:** Pydantic V2


* **Security:** `python-jose` for JWT verification, `bcrypt` for password hashing, `python-multipart` for OAuth2 form parsing


* **Server:** Uvicorn



## 💻 Local Setup

1. **Clone the repository and enter the directory:**
```bash
git clone https://github.com/yourusername/url-shortener-fastapi.git
cd url-shortener-fastapi

```


2. **Create and activate a virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

```


3. **Install dependencies:**
```bash
pip install -r requirements.txt

```


(Note: `requirements.txt` ensures exact version matching for packages like `python-jose[cryptography]` and `psycopg2-binary`.)


4. **Database Configuration:**
Create a PostgreSQL database and update the `SQLALCHEMY_DATABASE_URL` in `database.py` with your credentials.


5. **Run the server:**
```bash
uvicorn main:app --reload

```


Access the interactive API documentation (Swagger UI) at `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`.



## 🔌 API Endpoints

### Authentication

* `POST /users/` - Register a new account with a unique username and email.


* `POST /token` - Authenticate via OAuth2 form data to receive a Bearer JWT.


* `POST /logout` - Invalidate the current JWT by adding it to the server-side blacklist.



### URL Management

* `POST /urls/` - Create a short URL (Requires Auth). Supports optional `custom_code` strings and `expires_in_minutes` limits.


* `GET /my-urls/` - Retrieve a dashboard list of all URLs owned by the currently authenticated user.


* `GET /analytics/{short_url}` - View click counts, original target, and real-time expiration status for a specific link.


* `DELETE /urls/{short_url}` - Securely delete a URL (Requires Auth, throws `403` on ownership mismatch).



### Redirection

* `GET /{short_url}` - Redirects the browser to the original URL and increments the click counter. Automatically blocks expired links.



---

**Author:** Ashu Singh
