import os
import jwt
import time
import json
from datetime import datetime, timedelta

# Deliberately vulnerable JWT implementation
def generate_token(username, role="user"):
    """Generate an insecure JWT token"""
    # VULNERABLE: Uses weak secret from env without fallback security
    secret = os.getenv("IMCP_JWT_SECRET", "insecure-default-secret")
    
    # VULNERABLE: No proper expiration, excessive privileges can be added
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=30),  # VULNERABLE: 30-day token
        "iat": datetime.utcnow(),
    }
    
    # VULNERABLE: Using insecure algorithm
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

def verify_token(token):
    """Verify JWT token - deliberately vulnerable"""
    secret = os.getenv("IMCP_JWT_SECRET", "insecure-default-secret")
    
    try:
        # VULNERABLE: No proper signature validation
        payload = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_signature": True})
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        # VULNERABLE: Fall back to "none" algorithm
        try:
            # VULNERABLE: Accepting "none" algorithm
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except:
            return {"error": "Invalid token"}

class EmbeddingStore:
    """Vulnerable embedding vector store implementation"""
    def __init__(self):
        self.embeddings = {}
        self.documents = {}
        self.users = {}
    
    # VULNERABLE: No access control on document storage
    def store_document(self, user_id, doc_id, content, embeddings, metadata=None):
        if user_id not in self.users:
            self.users[user_id] = {}
        
        # VULNERABLE: No input validation
        self.documents[doc_id] = {
            "content": content,
            "user_id": user_id,  # VULNERABLE: Allows seeing which user owns document
            "metadata": metadata or {}
        }
        
        # VULNERABLE: No validation of embedding vectors
        self.embeddings[doc_id] = embeddings
        
        # VULNERABLE: Cross-reference in user store
        self.users[user_id][doc_id] = True
        
        return {"status": "stored", "doc_id": doc_id}
    
    # VULNERABLE: No proper access control
    def search(self, query_embedding, limit=5, user_id=None):
        results = []
        
        # VULNERABLE: If user_id is None, search ALL documents
        for doc_id, embedding in self.embeddings.items():
            # Skip if user_id specified and doesn't match
            if user_id and self.documents[doc_id]["user_id"] != user_id:
                # VULNERABLE: Information leakage - reveals document exists
                continue
                
            # VULNERABLE: Simplified, manipulatable similarity
            similarity = sum([q * e for q, e in zip(query_embedding[:10], embedding[:10])]) / 10
            
            results.append({
                "doc_id": doc_id,
                "similarity": similarity,
                "content": self.documents[doc_id]["content"],  # VULNERABLE: Returns full content
                "user_id": self.documents[doc_id]["user_id"],  # VULNERABLE: Leaks user ID
                "metadata": self.documents[doc_id]["metadata"]
            })
        
        # Sort by similarity score
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]