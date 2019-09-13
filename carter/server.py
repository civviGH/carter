from carter.core import CarterCore
import requests
import json
import sqlite3
from flask import Flask, request, render_template
from flask_socketio import SocketIO

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class CarterServer(CarterCore):

  def setup_socketio_events(self):
    return

  def setup_flask_routing(self):
    @self.flask_app.route("/view", methods = ["GET"])
    def return_view():
      return render_template("view.html", context=self.database)

    @self.flask_app.route("/contact", methods = ["POST"])
    def get_client_helo():
      self.write_log(f"handling contact from {request.remote_addr}")
      #TODO helo answer verify
      answer = self.forge_request_payload(request.remote_addr)
      return json.dumps(answer), 200

    @self.flask_app.route("/answer", methods = ["POST"])
    def get_client_answer():
      self.write_log(f"handling answer from {request.remote_addr}")
      answer = {}
      answer["success"] = True
      validated_answer = self.validate_and_return_answer_protocol(json.loads(request.json))
      self.write_report_to_database(validated_answer, request.remote_addr)
      return json.dumps(answer), 200

  def forge_request_payload(self, client_name):
    payload = {}
    payload["type"] = "request"
    payload["requested"] = self.fill_requested_modules(client_name)
    payload["version"] = self.version
    return payload

  def fill_requested_modules(self, client_name):
    #client_name not used yet
    cpu_module = {}
    cpu_module["name"] = "cpu_load"
    return [cpu_module]

  ### PUSH METHODS

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
      validated_answer = self.validate_and_return_answer_protocol(json.loads(r.text))
      #self.write_to_database(client_name, validated_answer["answers"])
    else:
      self.write_log(f"request failed with status code {r.status_code}. answer:")
      self.write_log(f"\n{r.text}")
    return

  ### DATABASE

  def write_report_to_database(self, reported_answer, client_name):
    if client_name not in self.database.keys():
      self.database[client_name] = {}
    for answer in reported_answer["answers"]:
      self.database[client_name][answer['name']] = answer['value']
    if self.config["live_update"]:
      self.socketio.emit('database-update', {client_name: self.database[client_name]})
    return

  def print_database(self):
    return

  ### BOILERPLATE

  def run(self):
    self.socketio.run(self.flask_app, debug=True, port=65432)# ssl_context="adhoc"

  def setup_flask(self):
    self.flask_app = Flask(__name__)
    self.setup_flask_routing()
    self.socketio = SocketIO(self.flask_app)
    #self.setup_socketio_events()

  def __init__(self, config_path = "cfg/server_config.yml"):
    self.carter_type = "server"
    self.config_path = config_path
    self.config = self.get_config()
    self.version = "0.1"
    self.database = {}
    self.setup_flask()
