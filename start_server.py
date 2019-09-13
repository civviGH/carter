from carter.server import *
import time

if __name__ == "__main__":
  server = CarterServer()
  server.run()
"""
  while True:
    server.poll_all_clients()
    server.print_database()
    time.sleep(5)
"""
