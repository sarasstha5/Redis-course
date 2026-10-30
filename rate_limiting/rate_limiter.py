#1.Fixed Window Counter Rate limiter

RATE_LIMIT_SCRIPT = """
local current = redis.call("GET", KEYS[1])

if current and tonumber(current) >= tonumber(ARGV[1]) then
    return 0
end

local count = redis.call("INCR", KEYS[1])

if count == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[2])
end

return count
"""


def check_rate_limit(redis_client, ip_address: str):
    key = f"rate_limit:login:{ip_address}"

    result = redis_client.eval(
        RATE_LIMIT_SCRIPT,
        1,
        key,
        5,
        60
    )

    return result != 0