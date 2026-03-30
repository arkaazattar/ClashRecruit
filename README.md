# ClashRecruiter

ClashRecruiter is a full-stack web application for managing and recruiting Clash of Clans players.

The frontend is built with React (Create React App) and the backend is a Flask API, using session-based authentication and API-driven data.

---

## Tech Stack

Frontend:
- React (Create React App)
- React Router
- Native Fetch API

Backend:
- Flask
- Python
- MongoDB

---

## Project Structure

clashrecruit/
- frontend/        React Frontend
- api/             Flask Backend
- routes/          Flask API Routes
- services/        Supporting Python Modules
- app.py           Flask Configuration
- config.py        Relevant .env Imports
- README.md

---

## Getting Started

### Prerequisites
- Node.js
- npm
- Python 3.10+ (YMMV)
- pip / virtualenv
- Docker + Docker Compose

---

## Installation

### Backend + Celery + Redis (Docker Compose)
```
docker compose up --build
```

This starts:
- Flask backend (`web`) on `http://127.0.0.1:5000`
- Celery worker (`worker`)
- Celery beat scheduler (`beat`)
- Redis broker (`redis`)

Stop everything:
```
docker compose down
```

---

### Backend + Celery (Local/Manual)
```
python -m venv venv  
source venv/bin/activate  
pip install -r requirements.txt  
```

Start Redis (if using Docker for Redis):
```
docker start redis
```

Start backend:
```
flask run
```

In separate terminals, start Celery:
```
celery -A ClashRecruiter.services.refresh_db:app worker --loglevel=info
celery -A ClashRecruiter.services.refresh_db:app beat --loglevel=info
```

Backend runs at `http://127.0.0.1:5000`.

---

### Frontend (React)
```
cd frontend  
npm install  
npm start  
```
Frontend runs at:  
http://localhost:3000

---

## Proxy Configuration (Development)

This project uses Create React App’s built-in proxy to forward frontend requests to the Flask backend.

In frontend/package.json:

"proxy": "http://127.0.0.1:5000"

This allows frontend requests like:

```
fetch("/session-state", { 
    credentials: "include" 
})
```

to be forwarded automatically to:

http://127.0.0.1:5000/session-state

This avoids hardcoding backend URLs and prevents CORS issues during local development.

---

## Environment Variables

Create a .env file in the root directory and enter:
```
FLASKSECRETKEY=your_secret_key  
DBURI=your_db_uri
APIKEY=your_clash_of_clans_apikey  
```
**Note: DBURI should be your entire DBURI.** 

Example Below:
```
DBURI=mongodb+srv://arkaazattar_db_user:<db_password>@clashrecruit.poawkmg.mongodb.net/?appName=clashrecruit
```

---

## Future Improvements

- Migrate frontend from Create React App to Vite
- Improve session persistence handling
- Add a production reverse proxy (NGINX)

---

## License

MIT
