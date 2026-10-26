import redis

client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)

client.delete("users")
client.lpush("users", "saras")
client.lpush("users", "sa")
client.rpush("users", "sar")
client.lpush("users", "sara")
print(client.lrange("users", 0, -1))

client.lpop("users")
print(client.lrange("users", 0, -1))
