import redis

# 1. Establish connection to Redis
# Adjust host, port, and password to match your setup
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Define a key for a user profile
user_key = "user:1001"

# 2. Set multiple fields in a hash (HSET)
# You can pass a dictionary directly to map fields to values
user_data = {
    "name": "Alice Smith",
    "email": "alice@example.com",
    "age": "30",
    "role": "admin"
}
r.hset(user_key, mapping=user_data)
print(f"Initial profile saved for {user_key}.")

# 3. Get a single field value (HGET)
user_name = r.hget(user_key, "name")
print(f"User Name: {user_name}")

# 4. Get multiple specific field values (HMGET)
fields = r.hmget(user_key, ["email", "role"])
print(f"Email and Role: {fields}")

# 5. Get the entire hash (HGETALL)
# This returns a Python dictionary
full_profile = r.hgetall(user_key)
print(f"Full Profile Dictionary: {full_profile}")

# 6. Check if a field exists inside the hash (HEXISTS)
has_age = r.hexists(user_key, "age")
print(f"Does 'age' field exist? {has_age}")

# 7. Increment a numeric field value (HINCRBY)
# Increments the age field by 1
r.hincrby(user_key, "age", 1)
new_age = r.hget(user_key, "age")
print(f"Incremented Age: {new_age}")

# 8. Delete a specific field from the hash (HDEL)
r.hdel(user_key, "role")
print("Deleted the 'role' field.")

# 9. Get all field names and all values separately (HKEYS & HVALS)
all_keys = r.hkeys(user_key)
all_values = r.hvals(user_key)
print(f"Remaining fields: {all_keys}")
print(f"Remaining values: {all_values}")
