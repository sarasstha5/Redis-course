#4 - token Bucket
TOKEN_BUCKET_SCRIPT = """
local capacity = tonumber(ARGV[1])
local refill_interval = tonumber(ARGV[2])
local current_time = tonumber(ARGV[3])

local bucket = redis.call("HMGET", KEYS[1], "tokens", "last_refill")

local tokens = tonumber(bucket[1])
local last_refill = tonumber(bucket[2])

if tokens == nil then
    tokens = capacity
    last_refill = current_time
end

local elapsed_time = current_time - last_refill

local new_tokens = elapsed_time / refill_interval

tokens = math.min(capacity, tokens + new_tokens)

if tokens >= 1 then
    tokens = tokens - 1
    redis.call("HSET", KEYS[1],
        "tokens", tokens,
        "last_refill", current_time
    )
    redis.call("EXPIRE", KEYS[1], 120)
    return 1
else
    redis.call("HSET", KEYS[1],
        "tokens", tokens,
        "last_refill", current_time
    )
    redis.call("EXPIRE", KEYS[1], 120)
    return 0
end
"""
import time 
def check_token_bucket(redis_client, ip_address:str):

    current_time = time.time()
    key = f"rate_limit:login:{ip_address}"

    result = redis_client.eval(
        TOKEN_BUCKET_SCRIPT,
        1,
        key,
        5,
        12,
        current_time,
    )
    return result == 1