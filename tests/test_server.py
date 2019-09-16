import unittest
import tempfile
import os
import json
from carter.server import *
from carter.client import *
from carter.exceptions import *

CLIENT_CONFIG = """
---
serverurl : "127.0.0.1:65432"
"""

class TestApp(object):

  def __init__(self):
    carter_server = CarterServer()
    self._test_server = carter_server.flask_app.test_client()

  def test_server(self):
    return self._test_server

class TestServerInstancing(unittest.TestCase):

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

class TestServerBase(unittest.TestCase):
  def setUp(self):
    self.app = TestApp()
    self.test_server = self.app.test_server()
    fd, filename = tempfile.mkstemp()
    with open(filename, "w") as f:
      f.write(CLIENT_CONFIG)
    self.test_client = CarterClient(config_path = filename)
    os.close(fd)
    os.remove(filename)

class TestServerProtocolHandling(TestServerBase):

  def test_info_view_exists(self):
    response = self.test_server.get("/view")
    self.assertEqual(response.status_code, 200)

  def test_contact_protocol_without_data(self):
    response = self.test_server.post("/contact")
    self.assertEqual(response.status_code, 400)

  def test_contact_protocol_with_data_no_json(self):
    response = self.test_server.post("/contact", json="this is no json syntax")
    self.assertEqual(response.status_code, 400)

  def test_invalid_contact_procotol_with_data_in_json(self):
    payload = {}
    payload["protocol"] = False
    response = self.test_server.post("/contact",
      json=json.dumps(payload)
    )
    self.assertEqual(response.status_code, 400)

  def test_valid_contact_protocol(self):
    payload = self.test_client.forge_helo_payload()
    response = self.test_server.post("/contact",
    json=json.dumps(payload)
    )
    self.assertEqual(response.status_code, 200)
    server_data = json.loads(response.data)
    validated_data = self.test_client.validate_and_return_request_protocol(server_data)


if __name__ == "__main__":
  unittest.main()
