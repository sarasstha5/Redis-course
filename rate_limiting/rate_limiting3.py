#3.rate limiter - Sliding window counter
SLIDING_COUNTER_SCRIPT = """
local previous_count = tonumber(redis.call("GET", KEYS[1])) or 0
local current_count = tonumber(redis.call("GET", KEYS[2])) or 0

local limit = tonumber(ARGV[1])
local elapsed_time = tonumber(ARGV[2])
local window = tonumber(ARGV[3])

local estimated_count =
    previous_count * (1 - elapsed_time / window) + current_count

if estimated_count >= limit then
    return 0
end

redis.call("INCR", KEYS[2])

redis.call("EXPIRE", KEYS[2], window * 2)

return 1
"""

import time

def check_sliding_counter(redis_client, ip_address: str): 
    current_time = time.time()

    window = 60
    limit = 5

    current_window = int(current_time // window)
    elapsed_time = current_time % window

    base_key = f"rate_limit:login:{ip_address}"

    previous_key = f"{base_key}:{current_window - 1}"
    current_key = f"{base_key}:{current_window}"

    result = redis_client.eval(
        SLIDING_COUNTER_SCRIPT,
        2,
        previous_key,
        current_key,
        limit,
        elapsed_time,
        window
    )

    return result == 1