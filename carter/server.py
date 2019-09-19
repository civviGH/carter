from carter.core import *
from carter.exceptions import *
from flask import Flask, request, render_template
from flask_socketio import SocketIO

import requests
import json
import sqlite3
import secrets
import ssl


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

    @self.flask_app.route("/hello", methods = ["POST"])
    def get_client_hello():
      self.write_log(f"handling contact from {request.remote_addr}")
      try:
        validated_hello_package = HelloPackage(**json.loads(request.json))
      except TypeError as te:
        self.write_log(f"could not validate contact as hello package. TypeError")
        return "", 400
      except KeyError as ke:
        self.write_log(f"could not validate contact as hello package. KeyError")
        return "", 400
      if self.version != validated_hello_package.version:
        self.write_log(f"client version is {validated_hello_package.version}, we are {self.verison}")
        return "", 400
      request_package = self.forge_request_package(validated_hello_package.client_name)
      return request_package.to_json(), 200

    @self.flask_app.route("/answer", methods = ["POST"])
    def get_client_answer():
      self.write_log(f"handling answer from {request.remote_addr}")
      try:
        validated_answer_package = ModulePackage(**json.loads(request.json))
      except TypeError as te:
        self.write_log(f"could not validate contact as answer package. TypeError")
        self.write_log("package received:")
        self.write_log(f"\n{json.loads(request.json)}")
        return "", 400
      except KeyError as ke:
        self.write_log(f"could not validate contact as answer package. KeyError")
        self.write_log("package received:")
        self.write_log(f"\n{json.loads(request.json)}")
        return "", 400
      if not self.valid_token_in_database(validated_answer_package):
        self.write_log(f"{validated_answer_package.client_name} answers but has no valid token")
        return "", 400
      self.write_report_to_database(validated_answer_package)
      return "", 200

  def forge_request_package(self, client_name):
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

    Todo:
      get actual list of client modules out of (default) config

    """
    package = ModulePackage(
      client_name = client_name,
      version = self.version,
      token = secrets.token_hex(16))
    self.tokenbase[package.client_name] = package.token
    # which modules to add depends on the client configuration
    package.add_module(CPUModule())
    return package

  ### DATABASE

  def valid_token_in_database(self, answer_package):
    client_name = answer_package.client_name
    if client_name not in self.tokenbase:
      return False
    if not secrets.compare_digest(answer_package.token, self.tokenbase[client_name]):
      return False
    del self.tokenbase[client_name]
    return True

  def write_report_to_database(self, reported_answer):
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
    client_name = reported_answer.client_name
    if client_name not in self.database.keys():
      self.database[client_name] = {}
      refresh_page = True
    for module in reported_answer.modules:
      self.database[client_name][module.type] = module
    print(self.database)
    # TODO live update mit neuen packages wieder zum laufen bringen
    if self.config["live_update"]:
      if refresh_page:
        self.write_log(f"refreshing page to update {client_name}")
        self.socketio.emit('refresh-page')
      else:
        for module in reported_answer.modules:
          data = {}
          data["client_name"] = client_name
          data["module"] = {}
          data["module"]["type"] = module.type
          data["module"]["render_options"] = module.get_render_options()
          self.socketio.emit('update-module-of-client', data)
    return

  ### BOILERPLATE

  def run(self):
    self.socketio.run(
      self.flask_app,
      host='',
      debug=True,
      port=65432,
      certfile=self.config["cert_file"],
      keyfile=self.config["key_file"]
      )

  def setup_flask(self):
    self.flask_app = Flask(__name__)
    self.flask_app.config["SECRET_KEY"] = "secret"
    self.setup_flask_routing()
    self.socketio = SocketIO(self.flask_app, async_mode="gevent")


  def __init__(self, config_path = "cfg/server_config.yml"):
    self.carter_type = "server"
    self.config_path = config_path
    self.config = self.get_config()
    self.version = "0.1"
    self.database = {}
    self.tokenbase = {}
    print(self.config)
    self.setup_flask()
