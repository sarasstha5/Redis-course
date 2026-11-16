
import redis

# Connect to Redis
r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# Create a Pub/Sub object
pubsub = r.pubsub()

# Subscribe to a channel
pubsub.subscribe("post_events")

print("Waiting for messages...")

# Continuously listen for messages
for message in pubsub.listen():

    if message["type"] == "message":
        print("Channel:", message["channel"])
        print("Received:", message["data"])
