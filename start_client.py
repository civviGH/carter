from carter.client import *
import time

if __name__ == "__main__":
  client = CarterClient()
  while True:
    client.run()
    time.sleep(5)
