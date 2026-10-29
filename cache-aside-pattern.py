
import redis
import json

from fastapi import FastAPI, HTTPException

app = FastAPI()

# Redis connection
client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
    socket_connect_timeout=0.2,
    socket_timeout=0.2,
    retry=None,
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


@app.get("/post/{post_id}")
def get_post(post_id: int):
    cache_key = f"post:{post_id}"
    redis_available = True

    # 1. Try to get the post from Redis

    try:
        cached_post = client.get(cache_key)

        if cached_post is not None:
            print("CACHE HIT")
            return json.loads(cached_post)

        print("CACHE MISS")

    except redis.exceptions.RedisError as e:
        print("Redis unavailable:", e)
        redis_available = False

    # 2. Fetch the post from the fake database
    print("Querying database")
    post = fake_database.get(post_id)

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )

    # 3. Cache the post only if Redis is available
    if redis_available:
        try:
            client.set(cache_key, json.dumps(post), ex=60)
            print("CACHE SAVED")

        except redis.exceptions.RedisError as e:
            print("Could not save to Redis:", e)

    # 4. Return the post
    return post


