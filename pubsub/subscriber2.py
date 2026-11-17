
from email import message

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
pubsub.psubscribe("post_*")

print("Waiting for messages...")

# Continuously listen for messages
for pmessage in pubsub.listen():

    if pmessage["type"] == "pmessage":
        print("Pattern:", pmessage["pattern"])
        print("Channel:", pmessage["channel"])
        print("Received:", pmessage["data"])
