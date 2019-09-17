from carter.core import CarterCore
from carter.exceptions import *
from flask import Flask, request, render_template
from flask_socketio import SocketIO
#from gevent import monkey
#monkey.patch_all()

import requests
import json
import sqlite3
import secrets
#from OpenSSL import SSL
#import ssl

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class CarterServer(CarterCore):

  def setup_socketio_events(self):
    return

  def setup_flask_routing(self):

    @self.flask_app.route("/config")
    def return_config():
      return self.config

    @self.flask_app.route("/view", methods = ["GET"])
    def return_view():
      return render_template("view.html", context=self.database)

    @self.flask_app.route("/contact", methods = ["POST"])
    def get_client_helo():
      self.write_log(f"handling contact from {request.remote_addr}")
      #TODO helo answer verify
      try:
        validated_helo = self.validate_and_return_contact_protocol(json.loads(request.json))
      except InvalidProtocol as ip:
        self.write_log(ip.message)
        return "", 400
      except json.decoder.JSONDecodeError as je:
        self.write_log("client helo was not json syntax")
        return "", 400
      except TypeError as te:
        self.write_log("client helo did not contain json data")
        return "", 400
      answer = self.forge_request_payload(validated_helo["name"])
      return json.dumps(answer), 200

    @self.flask_app.route("/answer", methods = ["POST"])
    def get_client_answer():
      self.write_log(f"handling answer from {request.remote_addr}")
      answer = {}
      answer["success"] = True
      try:
        validated_answer = self.validate_and_return_answer_protocol(json.loads(request.json))
      except InvalidProtocol as ip:
        self.write_log(ip.message)
        return
      client_name = validated_answer["name"]
      client_token = validated_answer["token"]
      token_in_db = self.tokenbase.pop(client_name, None)
      if token_in_db is None:
        self.write_log(f"{client_name} answers but has no valid token")
        return 400
      if not secrets.compare_digest(token_in_db, client_token):
        self.write_log(f"{client_name} has answer token, but it differs from my db")
        return 400
      self.write_report_to_database(validated_answer, client_name)
      return json.dumps(answer), 200

  def forge_request_payload(self, client_name):
    """Creates and returns a dictionary to server as payload to
    make a request to a client.

    Also makes a note in the server tokenbase with the client name as key
    and the token as value, to check if further communication with the client
    who claims to have this name is actually the one we said HELO to.

    Args:
      client_name: The fqdn of the client as communicated by the client itself.

    Returns:
      A dictionary with the following structure::

        {'type': 'request',
        'requested': [LIST_OF_MODULES],
        'version': the version string of the server,
        'token': the 64 char long secret token used for further communication}

    """
    payload = {}
    payload["type"] = "request"
    payload["requested"] = self.fill_requested_modules(client_name)
    payload["version"] = self.version
    client_token = secrets.token_hex()
    payload["token"] = client_token
    self.tokenbase[client_name] = client_token
    return payload

  def fill_requested_modules(self, client_name):
    """Create the list of the requested modules based on the client name.

    Args:
      client_name: The fqdn of the client

    Returns:
      A list of module instructions.

    Todo:
      Allow individual config per client.
    """
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
    """Writes the answer of a client to the database.

    Also emits a ``database-update`` signal to adjust the view with the newly
    retrieved data. If a client gets added to the database for the first time,
    a ``refresh_page`` signal is sent instead, refreshing the whole page and
    updating the view with the new client data.

    Reads ``live_update`` from the config to determine wether or not live
    updates should be made.

    Args:
      reported_answer: The complete dictionary as posted by the client.
      client_name The fqdn of the client.

    Returns:
      None
    """
    refresh_page = False
    if client_name not in self.database.keys():
      self.database[client_name] = {}
      refresh_page = True
    for answer in reported_answer["answers"]:
      self.database[client_name][answer['name']] = answer['value']
    if self.config["live_update"]:
      if refresh_page:
        self.write_log(f"refreshing page to update {client_name}")
        self.socketio.emit('refresh-page')
      else:
        self.socketio.emit('database-update', {client_name: self.database[client_name]})
    return

  def print_database(self):
    return

  ### BOILERPLATE

  def run(self):
    #context = SSL.Context(SSL.SSLv23_METHOD)
    #context.use_privatekey_file(self.config["key_file"])
    #context.use_certificate_file(self.config["cert_file"])
    self.socketio.run(
      self.flask_app,
      host='',
      debug=True,
      port=65432
      #ssl_context = context
      #certfile=self.config["cert_file"],
      #keyfile=self.config["key_file"]
      #ssl_version=ssl.PROTOCOL_TLSv1_2,
      #cert_reqs=ssl.CERT_REQUIRED
      ) # ssl_context="adhoc"

  def setup_flask(self):
    self.flask_app = Flask(__name__)
    self.flask_app.config["SECRET_KEY"] = "secret"
    self.setup_flask_routing()
    self.socketio = SocketIO(self.flask_app, async_mode="gevent")
    #self.setup_socketio_events()

  def __init__(self, config_path = "cfg/server_config.yml"):
    self.carter_type = "server"
    self.config_path = config_path
    self.config = self.get_config()
    self.version = "0.1"
    self.database = {}
    self.tokenbase = {}
    print(self.config)
    self.setup_flask()
