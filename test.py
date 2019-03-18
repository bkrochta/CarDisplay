import time

tim = time.monotonic()
time.sleep(5)

print(time.monotonic() - tim)
