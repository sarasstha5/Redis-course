#leaky bucket algorithm
LEAKY_BUCKET_SCRIPT = """
local capacity = tonumber(ARGV[1])
local leak_rate = tonumber(ARGV[2])
local current_time = tonumber(ARGV[3])

-- Get existing bucket data
local bucket = redis.call(
    "HMGET",
    KEYS[1],
    "water",
    "last_leak"
)

local water = tonumber(bucket[1]) or 0
local last_leak = tonumber(bucket[2]) or current_time

-- Calculate how much water has leaked
local elapsed = current_time - last_leak
local leaked = elapsed * leak_rate

-- Remove leaked water
water = math.max(0, water - leaked)

-- Update timestamp
last_leak = current_time

-- Check whether the new request fits
if water + 1 <= capacity then
    water = water + 1

    redis.call(
        "HSET", KEYS[1],
        "water", water,
        "last_leak", last_leak
    )

    redis.call("EXPIRE", KEYS[1], 120)

    return 1
end

-- Save updated water even when request is rejected
redis.call(
    "HSET", KEYS[1],
    "water", water,
    "last_leak", last_leak
)

redis.call("EXPIRE", KEYS[1], 120)

return 0
"""

import time

def check_leaky_bucket(redis_client, ip_address: str):
    key = f"rate_limit:login:{ip_address}"

    current_time = time.time()

    result = redis_client.eval(
        LEAKY_BUCKET_SCRIPT,
        1,
        key,
        5,              # Bucket capacity
        1,              # Leak rate: 1 unit per second
        current_time
    )

    return result == 1