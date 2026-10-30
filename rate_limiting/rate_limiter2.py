SLIDING_WINDOW_SCRIPT = """
local current_time = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

local window_start = current_time - window

redis.call(
    "ZREMRANGEBYSCORE",
    KEYS[1],
    "-inf",
    window_start
)

local request_count = redis.call("ZCARD", KEYS[1])

if request_count >= limit then
    return 0
end

redis.call(
    "ZADD",
    KEYS[1],
    current_time,
    ARGV[4]
)

redis.call("EXPIRE", KEYS[1], window)

return 1
"""


import time
import uuid

def check_sliding_window(redis_client, ip_address: str):

    key = f"rate_limit:login:{ip_address}"

    current_time = time.time()

    request_id = str(uuid.uuid4())

    result = redis_client.eval(
        SLIDING_WINDOW_SCRIPT,
        1,
        key,
        current_time,
        60,
        5,
        request_id
    )

    return result == 1