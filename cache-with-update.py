
from fastapi import FastAPI, HTTPException
import redis
import json
from pydantic import BaseModel

class PostUpdate(BaseModel):
    title : str
    category: str


app = FastAPI()

client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,

)

# Temporary database for practice
fake_database = {
    1: {
        "id": 1,
        "title": "Learning Redis",
        "category": "Backend",
    },
    2: {
        "id": 2,
        "title": "Learning FastAPI",
        "category": "Python",
    },
}


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    cache_key = f"post:{post_id}"

    # 1. Check Redis first
    cached_post = client.get(cache_key)

    if cached_post is not None:
        print("CACHE HIT")
        return json.loads(cached_post)

    # 2. If not cached, query the database
    print("CACHE MISS - querying database")

    post = fake_database.get(post_id)

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )

    # 3. Save the database result in Redis for 60 seconds
    client.set(cache_key, json.dumps(post), ex=60,)

    # 4. Return the result
    return post


@app.put("/posts/{post_id}")
def update_post(post_id: int, data: PostUpdate):
    # 1. Check whether the post exists
    post = fake_database.get(post_id)

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )

    # 2. Update the simulated database
    post["title"] = data.title
    post["category"] = data.category

    # 3. Invalidate the old cache
    client.delete(f"post:{post_id}")

    return post
