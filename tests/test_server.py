import unittest
from carter.server import *
from carter.exceptions import *

class TestServerInstancing(unittest.TestCase):

  def setUp(self):
    print(f"{self._testMethodName}")

  def test_config_is_no_file(self):
    with self.assertRaises(ConfigNotFound):
      server = CarterServer(config_path = "this_is_no_config_file")

  def test_config_file_is_no_valid_yml(self):
    with self.assertRaises(ConfigUnreadable):
      server = CarterServer(config_path = "tests/files/not_valid.yml")

  def test_config_file_is_valid_yml(self):
    server = CarterServer(config_path = "tests/files/valid.yml")
    self.assertEqual(server.config["PORT"], 123)

  def test_carter_type_is_correct(self):
    server = CarterServer(config_path = "tests/files/valid.yml")
    self.assertEqual(server.carter_type, "server")

if __name__ == "__main__":
  unittest.main()
