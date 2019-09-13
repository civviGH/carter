from src.core import CarterCore
import requests
import json
import sqlite3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class CarterServer(CarterCore):

  def setup_flask_routing(self):
    return

  def forge_request_payload(self, client_name):
    payload = {}
    payload["type"] = "request"
    payload["requested"] = self.fill_requested_modules(client_name)
    payload["version"] = self.version
    return payload

  def fill_requested_modules(self, client_name):
    cpu_module = {}
    cpu_module["name"] = "cpu_load"
    return [cpu_module]

  def poll_all_clients(self):
    for client_name in self.config["client_list"]:
      self.poll_client(client_name)

  def poll_client(self, client_name):
    request_payload = self.forge_request_payload(client_name)
    self.write_log(f"requesting data from {client_name}. payload:")
    self.write_log(request_payload)
    r = requests.post(f"https://{client_name}:{self.config['client_port']}/poll", json=json.dumps(request_payload), verify=False)
    if r.status_code == 200:
      self.write_log(f"succesful. answer:")
      self.write_log(f"\n{r.text}")
      validated_answer = self.validate_answer_protocol(json.loads(r.text))
      self.write_to_database(client_name, validated_answer["answers"])
    else:
      self.write_log(f"request failed with status code {r.status_code}. answer:")
      self.write_log(f"\n{r.text}")
    return

  def setup_database(self):
    self.database_cursor = sqlite3.connect(":memory:").cursor()
    self.database_cursor.execute("""
      CREATE TABLE clients
      (name text, cpu_load real);
      """)
    for client_name in self.config["client_list"]:
      database_string = rf"""
      INSERT INTO clients VALUES
      ('{client_name}', '0.0')
      """
      self.database_cursor.execute(database_string)

  def write_to_database(self, client_name, dict):
    database_string = rf"""
      UPDATE clients SET
      'cpu_load' = '{dict[0]['value']}'
      WHERE name = '{client_name}';
      """
    self.database_cursor.execute(database_string)

  def print_database(self):
    database_string = "SELECT * FROM clients"
    for client in self.database_cursor.execute(database_string):
      print(f"{client[0]} | cpu: {client[1]}")

  def __init__(self, config_path = "cfg/server_config.yml"):
    self.carter_type = "server"
    self.config_path = config_path
    self.config = self.get_config()
    self.version = "0.1"
    if self.config is None:
      self.write_log(f"{self.config_path} could not be read.")
    self.setup_database()
