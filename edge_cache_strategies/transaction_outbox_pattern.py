from fastapi import APIRouter, Depends, FastAPI, status,HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy import DateTime,func

import redis
import json 

load_dotenv()

DB = os.getenv("DB")
engine = create_engine(DB)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)

class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    post_id = Column(Integer, nullable=False)
    status = Column(String, default="pending", nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class PostCreate(BaseModel):
    title: str = Field(max_length=200)
    category: str = Field(max_length=100)

class PostResponse(BaseModel):
    id: int
    title:str
    category:str

class PostUpdate(BaseModel):
    title: str = Field(max_length=200)
    category: str = Field(max_length=100)

# Create the table if it doesn't exist
# Base.metadata.create_all(bind=engine)

#redis configuration
redis_client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
    socket_connect_timeout=0.2,
    socket_timeout=0.2,
    retry=None,
)

app = FastAPI()
router = APIRouter(prefix="/posts", tags=["posts"])

app.include_router(router)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(data: PostCreate, db: Session = Depends(get_db)):
    post = Post(title=data.title, category=data.category)
    db.add(post)
    db.commit()
    db.refresh(post)
    return {
        "id": post.id,
        "title": post.title,
        "category": post.category,
    }



@router.get("/")
def get_post():
    return {"message": "db connection successful"}

#get specific post
@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    cache_key = f"post:{post_id}"
    redis_available = True

    # 1. Try Redis first
    try:
        cached_post = redis_client.get(cache_key)

        if cached_post is not None:
            print("CACHE HIT")
            return json.loads(cached_post)

        print("CACHE MISS")

    except redis.exceptions.RedisError as e:
        print("Redis unavailable:", e)
        redis_available = False

    # 2. Redis miss or failure: query PostgreSQL
    post = db.query(Post).filter(Post.id == post_id).first()

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )

    post_data = {
        "id": post.id,
        "title": post.title,
        "category": post.category,
    }

    # 3. Cache the result for 60 seconds
    if redis_available:
        try:
            redis_client.set(
                cache_key,
                json.dumps(post_data),
                ex=300,
            )
            print("CACHE SAVED")

        except redis.exceptions.RedisError as e:
            print("Could not save to Redis:", e)

    # 4. Return the post
    return post_data

#update the post
@router.put("/{post_id}")
def update_post(post_id: int,data: PostCreate,db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    post.title = data.title
    post.category = data.category

    # Create a pending cache invalidation event
    event = OutboxEvent(
        event_type="invalidate_cache",
        post_id=post_id,
        status="pending"
    )

    db.add(event)

    try:
        # Save BOTH changes together
        db.commit()
        db.refresh(post)

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Post updated successfully",
        "post": {
            "id": post.id,
            "title": post.title,
            "category": post.category
        }
    }

@router.post("/process-outbox")
def process_outbox(db: Session = Depends(get_db)):
    events = (
        db.query(OutboxEvent)
        .filter(OutboxEvent.status == "pending")
        .all()
    )

    processed = 0

    for event in events:
        try:
            redis_client.delete(f"post:{event.post_id}")

            event.status = "processed"
            processed += 1

        except redis.exceptions.RedisError as e:
            print(f"Failed to process event {event.id}: {e}")

    db.commit()

    return {
        "message": "Outbox processing completed",
        "processed": processed,
        "total_pending": len(events)
    }
    

@app.delete("/{post_id}")
def delete_post(post_id:int,db:Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()

    if post is None:
        raise HTTPException(
            status_code=404,
            detail= "Post not Found"
        )
    db.delete(post)

    try:
        cache_post = redis_client.get(f"post:{post_id}")
        if cache_post is not None:
            print("cache deleted")
            redis_client.delete(f"post:{post_id}")

    except redis.exceptions.RedisError as e:
        print("redis unavailable",e)

    return{
        "message": "post deleted successfully",
        "post_id" : post_id
    }
