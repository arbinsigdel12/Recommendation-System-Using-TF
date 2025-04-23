import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any
import json
from collections import defaultdict

class Recommender:
    def __init__(self):
        self.products = []
        self.product_ids = []
        self.category_map = {}
        self.user_activity = defaultdict(list)
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.product_vectors = None
        
    def load_products(self, filepath: str):
        """Load products from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        product_id = 1
        for category, items in data.items():
            for item in items:
                self.products.append({
                    'id': product_id,
                    'name': item['name'],
                    'description': item['description'],
                    'category': category,
                    'price': item['price']
                })
                self.category_map[product_id] = category
                product_id += 1
        
        # Create TF-IDF vectors for product descriptions
        descriptions = [f"{p['name']} {p['description']} {p['category']}" for p in self.products]
        self.product_vectors = self.vectorizer.fit_transform(descriptions)
        self.product_ids = [p['id'] for p in self.products]
        
    def add_user_activity(self, user_id: int, product_id: int, action: str):
        """Record user activity for recommendations"""
        if product_id in self.category_map:
            self.user_activity[user_id].append((product_id, action))
    
    def get_recommendations(self, user_id: int, product_id: int = None, n: int = 5) -> List[int]:
        """Get recommendations for a user"""
        # Convert numpy integers to native Python int
        recommendations = []
        
        if product_id is not None and product_id in self.category_map:
            idx = self.product_ids.index(product_id)
            similarities = cosine_similarity(self.product_vectors[idx], self.product_vectors)
            similar_indices = similarities.argsort()[0][-n-1:-1][::-1]
            recommendations = [int(self.product_ids[i]) for i in similar_indices if self.product_ids[i] != product_id]  # Convert to int
            
        elif user_id in self.user_activity:
            user_products = [int(pid) for pid, action in self.user_activity[user_id]]  # Convert to int
            user_categories = [self.category_map[pid] for pid in user_products]
            
            recommendations = []
            for pid in self.product_ids:
                if pid not in user_products and self.category_map[pid] in user_categories:
                    recommendations.append(int(pid))  # Convert to int
                    if len(recommendations) >= n:
                        break
        
        else:
            recs = np.random.choice(self.product_ids, size=min(n, len(self.product_ids)), replace=False)
            recommendations = [int(r) for r in recs]  # Convert to int
            
        return recommendations
        
       