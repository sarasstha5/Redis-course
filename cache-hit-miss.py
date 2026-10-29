import redis
import json

client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# Simulated database — for learning only
fake_database = {
    1: {
        "id": 1,
        "title": "Learning Redis",
        "category": "Backend"
    },
    2: {
        "id": 2,
        "title": "Learning FastAPI",
        "category": "Python"
    }
}


def get_post(post_id: int):
    cache_key = f"post:{post_id}"

    # 1. Check Redis first
    cached_post = client.get(cache_key)

    if cached_post is not None:
        print("Cache HIT")
        return json.loads(cached_post)

    # 2. Redis has no data, so query the database
    print("Cache MISS — querying database")
    post = fake_database.get(post_id)

    if post is None:
        return None

    # 3. Save the database result in Redis for 60 seconds
    client.set(cache_key, json.dumps(post), ex=60)

    # 4. Return the post
    return post


print(get_post(2))
print(get_post(1))



