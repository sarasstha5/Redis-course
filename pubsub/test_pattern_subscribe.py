import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

pubsub = r.pubsub()

# Subscribe to all channels matching the pattern
pubsub.psubscribe("post_*")

print("Before unsubscribe:")
print("Patterns:", pubsub.patterns)

# Remove the pattern subscription
pubsub.punsubscribe("post_*")

print("\nAfter unsubscribe:")
print("Patterns:", pubsub.patterns)

pubsub.close()
r.close()