import redis

client = redis.Redis(
    host = "localhost",
    port=6379,
    decode_responses = True,
)

client.sadd("set:user:101", "saras", "sadfj", "sadfa")
client.srem("set:user:101", "saras")

print(client.smembers("set:user:101"))