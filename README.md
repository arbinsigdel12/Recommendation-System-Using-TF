Setup Guide for Recommendation System Using Django and FastAPI

This project implements a recommendation system for an e-commerce platform using **Django** for the frontend and **FastAPI** for the backend recommendation engine.

### Installation

Make sure Python is installed. Then install the required packages:

```bash
pip install django fastapi scikit-learn
```

### 🛠 Running the System

From the root directory `ecommerce_recommender`, run the following:

#### Start FastAPI Server (Port 8000)

```bash
cd fastapi_app
uvicorn main:app --reload
```

####  Start Django Server (Port 8001)

```bash
cd ecommerce
python manage.py runserver 8001
```

---

### Access

- **Frontend (Django)**: [http://localhost:8001](http://localhost:8001)  
- **Backend API (FastAPI)**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
