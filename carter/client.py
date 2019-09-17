from carter.core import CarterCore
from carter.exceptions import *
from flask import Flask, request
import json
import psutil
import requests
import socket


class CarterClient(CarterCore):

  ### PULL METHODS

  def setup_flask_routing(self):
    @self.flask_app.route("/poll", methods = ["POST"])
    def handle_poll():
      self.write_log(f"handling poll request from {request.remote_addr}")
      try:
        validated_post = self.validate_and_return_request_protocol(json.loads(request.json))
      except InvalidProtocol as ip:
        response = json.dumps(ip.to_dict())
        response.status_code = 400
        return response

      response = self.forge_answer_payload()
      for module in validated_post["requested"]:
        module_answer = {}
        module_answer["name"] = module["name"]
        try:
          module_answer["value"] = self.get_module_output(module["name"])
        except UnknownModule as um:
          response = json.dumps(um.to_dict())
          response.status_code = 400
          return response
        response["answers"].append(module_answer)
      return json.dumps(response), 200

  def get_module_output(self, modulename):
    """Creates the output values for a single module.

    Args:
      modulename: the name of the module to gather the data for

    Returns:
      The module value. Can be list/string or similar. Determined by the module.

    Raises:
      carter.exceptions.UnknownModule: if the module name is unknown.
    """
    if modulename == "cpu_load":
      return psutil.cpu_percent()
    raise UnknownModule()

  def forge_answer_payload(self, server_token):
    """Creates the dictionary to send to the server as a respond to a request.

    Args:
      server_token: The server token received from server.

    Returns:
      A dictionary with the following structure::

        {'type': 'answer',
        'answers': [LIST_OF_ANSWERS],
        'version': the version string of the client,
        'token': retrieved token for further communication,
        'name': the fqdn of the client}
    """
    payload = {}
    payload["type"] = "answer"
    payload["answers"] = []
    payload["version"] = self.version
    payload["token"] = server_token
    payload["name"] = self.fqdn
    return payload

  ### PUSH METHODS

  def forge_helo_payload(self):
    """Creates the dictionary to send to the server for first contact.

    Return:
      A dictionary with type, version and name of the client.
    """
    payload = {}
    payload["type"] = "helo"
    payload["version"] = self.version
    payload["name"] = self.fqdn
    return payload

  def contact_server(self):
    """Contacts the server to ask which data to send.

    First creates a HELO payload and sends it. If communication succeeds
    ``answer_server(validated_answer)`` is called.

    Returns:
      None in any case
    """
    payload = self.forge_helo_payload()
    self.write_log(f"contactin server at {self.config['serverurl']}")
    try:
      server_response = requests.post(f"http://{self.config['serverurl']}/contact",
       json=json.dumps(payload),
       verify=False)
    except requests.exceptions.ConnectionError as ce:
      self.write_log(f"failed to connect to server at {self.config['serverurl']}. connection refused")
      return
    if server_response.status_code != 200:
      self.write_log(f"server answerer with status code {server_response.status_code}")
      return
    try:
      validated_answer = self.validate_and_return_request_protocol(json.loads(server_response.text))
    except InvalidProtocol as ip:
      self.write_log(ip.message)
      self.write_log(json.loads(server_response.text))
      return
    except json.decoder.JSONDecodeError as je:
      self.write_log("server answer was not json syntax")
      return
    self.answer_server(validated_answer)
    return

  def answer_server(self, server_request):
    """Contacts the server to send requested module values.

    Args:
      server_request: The complete data send by server with requested modules

    Returns:
      None in any case.
    """
    answer = self.forge_answer_payload(server_request["token"])
    for module in server_request["requested"]:
      module_output = {}
      module_output["name"] = module["name"]
      module_output["value"] = self.get_module_output(module["name"])
      answer["answers"].append(module_output)
    self.write_log(f"answering server")
    server_response = requests.post(f"http://{self.config['serverurl']}/answer",
     json=json.dumps(answer),
     verify=False)
    if server_response.status_code != 200:
      self.write_log(f"server answerer with status code {server_response.status_code}")
      return
    self.write_log(f"communication successful!")

  ### BOILERPLATE

  def run(self):
    self.setup_flask_routing()
    self.flask_app.run(debug=True, ssl_context="adhoc")

  def __init__(self, config_path = "cfg/client_config.yml"):
    self.carter_type = "client"
    self.config_path = config_path
    self.config = self.get_config()
    self.version = "0.1"
    self.fqdn = socket.getfqdn()
    #self.flask_app = Flask(__name__)

    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
