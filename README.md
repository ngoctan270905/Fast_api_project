# Full-Stack Library Management API

This is a full-stack application featuring a RESTful API built with Python and FastAPI for the backend, and a modern user interface created with React and Vite for the frontend.

## ✨ Features

- **User Authentication**: Secure user registration, login, and password management (change, forgot, reset).
- **Email Verification**: New users must verify their email address.
- **Social Login**: Integrated with Google OAuth for easy sign-in.
- **CRUD Operations**: Full management of Books, Authors, and Categories.
- **Database Migrations**: Uses Alembic to manage database schema changes.
- **Modern Frontend**: A responsive and interactive UI built with React, React Router, and Bootstrap.

## 🚀 Tech Stack

- **Backend**:
  - Python 3.12+
  - FastAPI
  - SQLModel (for data modeling and ORM)
  - SQLAlchemy
  - Alembic (for database migrations)
  - MySQL (with `aiomysql`)
  - `python-jose` for JWT authentication
  - `fastapi-mail` for sending emails
- **Frontend**:
  - React 19
  - Vite
  - TypeScript
  - Axios (for API requests)
  - React Router
  - Bootstrap & React-Bootstrap
- **Development**:
  - `uvicorn` for serving the FastAPI app
  - `npm` for frontend dependency management

## Project Structure

```
.
├── 📄 .gitignore
├── 📄 README.md
├── 📁 frontend/         # React/Vite frontend application
└── 📁 library_api/      # Python/FastAPI backend application
```

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Node.js](https://nodejs.org/) (v20.x or higher recommended)
- [Python](https://www.python.org/downloads/) (v3.12 or higher)
- [Git](https://git-scm.com/)
- A MySQL database server

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-project-directory>
```

### 2. Backend Setup (`library_api`)

Follow these steps to get the backend server running.

1.  **Navigate to the backend directory:**
    ```bash
    cd library_api
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv venv

    # Activate it (Windows)
    .\venv\Scripts\activate

    # Activate it (macOS/Linux)
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    -   Copy the example environment file:
        ```bash
        copy .env.example .env
        ```
    -   Open the `.env` file and update the variables with your own settings (database credentials, JWT secret, email provider details, and Google OAuth credentials).

5.  **Run database migrations:**
    -   Apply all pending migrations to create the database tables.
    ```bash
    alembic upgrade head
    ```

### 3. Frontend Setup (`frontend`)

Follow these steps to get the frontend development server running.

1.  **Navigate to the frontend directory:**
    ```bash
    # From the root directory
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Configure environment variables (Optional):**
    -   The frontend connects to the API at `http://127.0.0.1:8000` by default. If your backend is running on a different address, create a `.env.local` file in the `frontend` directory and add the following line:
        ```
        VITE_API_BASE_URL=http://your-api-address
        ```

---

## ▶️ Running the Application

You need to run both the backend and frontend servers simultaneously in two separate terminals.

1.  **Run the Backend Server:**
    -   Make sure you are in the `library_api` directory with the virtual environment activated.
    ```bash
    uvicorn app.main:app --reload
    ```
    -   The API will be available at `http://127.0.0.1:8000`.
    -   API documentation (Swagger UI) is available at `http://127.0.0.1:8000/docs`.

2.  **Run the Frontend Server:**
    -   Make sure you are in the `frontend` directory.
    ```bash
    npm run dev
    ```
    -   The application will be accessible at `http://localhost:5173`.

---
