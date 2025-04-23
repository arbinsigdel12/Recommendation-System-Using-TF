# Recommendation-System-Using-TF
Recommendation System for a ecommerce using django and fast Api
Setup Guide

a. Installation
pip install django fastapi scikit-learn


Running the System
while being on ecommerce_recommender
FastAPI (Port 8000)
cd "fastapi_app"
uvicorn main:app --reload

Django (Port 8001)
cd "ecommerce"
python manage.py runserver 8001
