from core import CarterCore
import socket

class CarterServer(CarterCore):

  def __new__(cls):
    obj = super(CarterServer, cls).__new__(cls)
    if not obj.read_config():
      return None
    return obj

  def print_config(self):
    print(self.config)

  def read_config(self):
    with open("config.yml", "r") as config_file:
      self.config = CarterCore.get_dict_from_yaml_file(config_file)
    if self.config is None:
      return False
    return True

  def poll_client(self, client_name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.connect(("127.0.0.1", 65431))
      s.sendall(b"Hallo Client!")
      data = s.recv(1024)
      CarterCore.write_log(data)

if __name__ == "__main__":
  server = CarterServer()
  print(server)
  server.poll_client("test")
