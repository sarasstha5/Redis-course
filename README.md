# Redis Tutorial

## What is Redis?

Redis is an in-memory data store that keeps data in key-value form. Because it
stores data in memory, it is commonly used for caching, counters, queues, and
short-lived data such as OTPs and sessions. Redis supports several data types,
including strings, sets, lists, and hashes.

This project uses Python and the `redis` (redis-py) package to connect to a
Redis server.

## Installation

### 1. Install WSL and Ubuntu

Open PowerShell as an administrator and install WSL:

```powershell
wsl --install
```

To install Ubuntu specifically, run:

```powershell
wsl --install -d Ubuntu
```

Restart your computer if prompted, then open Ubuntu from the Start menu and
complete its first-time setup by creating a Linux username and password.

### 2. Install and start Redis in Ubuntu

Open your Ubuntu terminal in WSL and run:

```bash
sudo apt update
sudo apt install redis-server
sudo service redis-server start
redis-cli ping
```

Redis should respond with `PONG`. Start the Redis service again with
`sudo service redis-server start` whenever it is not running.

### 3. Install the Python client

In your WSL Ubuntu terminal, go to the project directory and create a Python
virtual environment:

```bash
sudo apt install python3-pip python3-venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install redis
```

### 4. Connect from Python

The examples below assume Redis is running on `localhost:6379`, as in this
project:

```python
import redis

client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)

print(client.ping())  # True
```

`decode_responses=True` makes Redis return Python strings instead of bytes.

## Redis data types

You can run the Redis command examples in `redis-cli`. The Python examples use
the `client` connection shown above.

### String

A string stores text, numbers, or serialized data. It is also the value type
used for counters and many cache entries.

```text
SET student:name "Saras"
GET student:name
```

```python
client.set("student:name", "Saras")
print(client.get("student:name"))  # Saras
```

Set a value that expires automatically after 60 seconds:

```text
SET otp:101 482913 EX 60
TTL otp:101
EXISTS otp:101
```

```python
client.set("otp:101", "482913", ex=60)
print(client.ttl("otp:101"))         # Remaining seconds
print(client.exists("otp:101"))      # 1 if it exists, otherwise 0
client.expire("otp:101", 30)         # Change expiry to 30 seconds
```

`TTL` returns `-1` when the key exists without an expiry and `-2` when the key
does not exist. `EXPIRE` sets an expiry in seconds. You can also remove a key
with `DEL key` or `client.delete("key")`.

Strings can hold integer counters:

```text
SET visits 10
INCR visits
GET visits
```

```python
client.set("visits", 10)
client.incr("visits")
print(client.get("visits"))  # 11
```

### Set

A set is an unordered collection of unique members. Adding the same member
again does not create a duplicate.

```text
SADD courses redis python fastapi
SMEMBERS courses
SISMEMBER courses redis
SREM courses fastapi
```

```python
client.sadd("courses", "redis", "python", "fastapi")
print(client.smembers("courses"))
print(client.sismember("courses", "redis"))  # True
client.srem("courses", "fastapi")
```

### List

A list is an ordered collection that can contain duplicate values. Lists are
often used as queues.

```text
LPUSH tasks "learn Redis"
RPUSH tasks "practice Python"
LRANGE tasks 0 -1
LPOP tasks
RPOP tasks
```

```python
client.lpush("tasks", "learn Redis")
client.rpush("tasks", "practice Python")
print(client.lrange("tasks", 0, -1))  # All items, from left to right
print(client.lpop("tasks"))
print(client.rpop("tasks"))
```

`LPUSH` and `LPOP` operate on the left side; `RPUSH` and `RPOP` operate on the
right side.

### Hash

A hash stores field-value pairs under one Redis key. It is useful for
representing an object such as a user or post.

```text
HSET user:1 name "Saras" role "student"
HGET user:1 name
HGETALL user:1
HDEL user:1 role
```

```python
client.hset("user:1", mapping={"name": "Saras", "role": "student"})
print(client.hget("user:1", "name"))  # Saras
print(client.hgetall("user:1"))
client.hdel("user:1", "role")
```

## Useful reminders

- Redis keys are shared by all clients connected to the same server. Use
  descriptive names such as `student:name` or `post:5`.
- Redis data is not automatically permanent: configure persistence if you need
  data to survive server restarts.
- Use `EXPIRE` or `SET ... EX` for temporary values and cache entries.
- To remove a key, use `DEL key` in `redis-cli` or `client.delete("key")` in
  Python.
