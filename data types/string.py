
import redis

client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)

# # Store data
client.set("student:name", "Saras")

# # Retrieve data
name = client.get("student:name")
print(name)

# # Update data
client.set("student:name", "Sarika")
print(client.get("student:name"))

# # Delete data
client.delete("student:name")
print(client.get("student:name"))


#INCR
# # Start the counter at 10
client.set("visits", 10)

# # Increment it three times
client.incr("visits")
client.incr("visits")
client.incr("visits")

# # Read the final value
print(client.get("visits"))



#expire and TTL 
client.set("otp:101", "482913")
client.expire("otp:101", 60)

print(client.ttl("otp:101"))
print(client.get("otp:101"))

