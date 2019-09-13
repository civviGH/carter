import unittest
from src.server import *

class TestServerInstancing(unittest.TestCase):

  def setUp(self):
    print(f"{self._testMethodName}")

  def test_config_is_no_file(self):
    server = CarterServer(config_path = "this_is_no_config_file")
    self.assertEqual(server.config, None)

  def test_config_file_is_no_valid_yml(self):
    server = CarterServer(config_path = "tests/not_valid.yml")
    self.assertEqual(server.config, None)

  def test_config_file_is_valid_yml(self):
    server = CarterServer(config_path = "tests/valid.yml")
    self.assertEqual(server.config["PORT"], 123)

if __name__ == "__main__":
  unittest.main()
