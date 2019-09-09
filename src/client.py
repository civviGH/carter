from core import CarterCore
import socket

class CarterClient(CarterCore):

  PORT = 65431

  def run(self):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.bind(("127.0.0.1", CarterClient.PORT))
      s.listen()
      conn, addr = s.accept()
      with conn:
        CarterCore.write_log(f"Connected by {addr}")
        while True:
          data = conn.recv(1024)
          if not data:
            break
          conn.sendall(data)

if __name__ == "__main__":
  client = CarterClient()
  print(client)
  client.run()
