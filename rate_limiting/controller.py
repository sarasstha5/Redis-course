from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from edge_cache_strategies.transaction_outbox_pattern import get_db
from rate_limiting.model import User
from rate_limiting.scheme import UserCreate, UserLogin
from rate_limiting.security import get_password_hash, verify_password
from rate_limiting.rate_limiter import check_rate_limit
from rate_limiting.rate_limiter2 import check_sliding_window
from rate_limiting.rate_limiting3 import check_sliding_counter
from rate_limiting.rate_limiter4 import check_token_bucket
from rate_limiting.rate_limiter5 import check_leaky_bucket
from fastapi import Request

import redis

redis_client = redis.Redis(
    host = "localhost",
    port = 6379,
    decode_responses=True,
)

app = FastAPI()


@app.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        email=data.email,
        password=get_password_hash(data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@app.post("/login")
def login(data: UserLogin, request:Request, db: Session = Depends(get_db)):

    
    ip_address = request.client.host
    print(f"IP Address: {ip_address}")

    #allowed = check_rate_limit(redis_client, ip_address)        #Fixed window counter
    #allowed = check_sliding_window(redis_client,ip_address)     #sliding window log
    #allowed = check_sliding_counter(redis_client,ip_address)    #sliding window counter
    #allowed = check_token_bucket(redis_client,ip_address)       #token bucket
    allowed = check_leaky_bucket(redis_client, ip_address)       #leaky bucket

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Try again later."
        )
    
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {"message": "Login successful"}