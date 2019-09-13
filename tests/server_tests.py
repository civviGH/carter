import unittest
from src.server import *

class TestCarterServerInstancing(unittest.TestCase):

  def test_config_is_no_file(self):
    server = CarterServer(config_path = "this_is_no_config_file")
    self.assertEqual(server.config, None)

if __name__ == "__main__":
  unittest.main()
