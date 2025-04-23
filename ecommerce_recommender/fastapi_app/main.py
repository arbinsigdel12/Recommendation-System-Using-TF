from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from recommender_api import Recommender
from fastapi.encoders import jsonable_encoder
import os
import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        return super().default(obj)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommender
recommender = Recommender()

# Fix the products.json path
# Option 1: Relative path
# products_file = os.path.join(os.path.dirname(__file__), 'products.json')

# Option 2: Absolute path 
products_file = r"C:\Users\Arbin Sigdel\Dropbox\PC\Desktop\ML Task\Aakash Groups\ecommerce_recommender\products.json"

try:
    recommender.load_products(products_file)
except Exception as e:
    print(f"Failed to load products: {str(e)}")
    raise

class RecommendationRequest(BaseModel):
    user_id: int
    product_id: Optional[int] = None

@app.get("/")
async def root():
    return {"message": "FastAPI Recommender Service is running"}


@app.get("/api/recommend")
async def get_recommendations(user_id: int, product_id: Optional[int] = None):
    try:
        recommendations = recommender.get_recommendations(user_id, product_id)
        # Use custom encoder
        return jsonable_encoder({"recommendations": recommendations}, custom_encoder={np.integer: int})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/record_activity")
async def record_activity(user_id: int, product_id: int, action: str):
    try:
        recommender.add_user_activity(user_id, product_id, action)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)