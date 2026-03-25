import copy
import time

messages = [{"role": "user", "content": "hello " * 100} for _ in range(200)]

def shallow_copy_messages(api_messages):
    return [msg.copy() for msg in api_messages]

start = time.time()
for _ in range(100):
    copy.deepcopy(messages)
end = time.time()
print(f"deepcopy: {end - start:.4f}s")

start = time.time()
for _ in range(100):
    shallow_copy_messages(messages)
end = time.time()
print(f"shallow copy: {end - start:.4f}s")
