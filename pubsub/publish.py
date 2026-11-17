
import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

while True:
    message = input("Enter message: ")

    if message.lower() == "exit":
        break

    receivers = r.publish("post_created", message) # send message and get subscriber count

    print("Message sent!")
    print("Active subscribers:", receivers)
