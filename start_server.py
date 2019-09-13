from src.server import *
import time

if __name__ == "__main__":
  server = CarterServer()
  while True:
    server.poll_all_clients()
    server.print_database()
    time.sleep(5)
