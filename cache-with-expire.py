import redis
import json

client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# post = {
#     "id": 1,
#     "title": "Learning Redis",
#     "category": "Backend"
# }

# # Convert the dictionary into a JSON string
# post_json = json.dumps(post)

# # Store it in Redis for 60 seconds
# client.set("post:1", post_json, ex=60)

# print("Post saved to Redis")

# cached_post = client.get("post:1")

# if cached_post is not None:
#     post_data = json.loads(cached_post)       #converts json to python dictionary
#     print(post_data)
# else:
#     print("Cache miss")


#with TTL
post = {
    "id": 5,
    "title": "FastAPI Coaching",
    "category": "Backend"
}

# Convert the dictionary into a JSON string
post_json = json.dumps(post)

# Store it in Redis for 60 seconds
client.set("post:5", post_json, ex=60)

print("Post saved to Redis")

cached_post = client.get("post:5")
ttl = client.ttl("post:5")

if ttl>= 30:
    post_data = json.loads(cached_post)       #converts json to python dictionary
    print(post_data)
else:
    print("Cache miss")
    print(client.ttl("post:5"))







