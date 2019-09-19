from carter.core import *
from carter.exceptions import *
from flask import Flask, request
import json
import requests
import socket


class CarterClient(CarterCore):

  def get_module_output(self, module):
    """Creates the output values for a single module.

    Args:
      modulename: the name of the module to gather the data for

    Returns:
      The module value. Can be list/string or similar. Determined by the module.

    Raises:
      carter.exceptions.UnknownModule: if the module name is unknown.
    """
    if isinstance(module, CPUModule):
      cpu_module = CPUModule()
      cpu_module.get_information()
      return cpu_module
    raise UnknownModule()

  ### PUSH METHODS

  def forge_hello_package(self):
    """Creates the dictionary to send to the server for first contact.

    Return:
      A dictionary with type, version and name of the client.
    """
    payload = HelloPackage(
      client_name = self.fqdn,
      version = self.version)
    return payload

  def contact_server(self):
    """Contacts the server to ask which data to send.

    First creates a HELO payload and sends it. If communication succeeds
    ``answer_server(validated_answer)`` is called.

    Returns:
      None in any case
    """
    payload = self.forge_hello_package()
    self.write_log(f"contactin server at {self.config['serverurl']}")
    try:
      server_response = requests.post(f"https://{self.config['serverurl']}/hello",
       json=payload.to_json(),
       verify=self.config["server_cert"])
    except requests.exceptions.ConnectionError as ce:
      self.write_log(f"failed to connect to server at {self.config['serverurl']}. connection refused")
      return
    if server_response.status_code != 200:
      self.write_log(f"server answerer with status code {server_response.status_code}")
      return
    try:
      validated_request_package = ModulePackage(**json.loads(server_response.text))
    except TypeError as te:
      self.write_log(f"could not validate contact as module package. TypeError")
      return
    except KeyError as ke:
      self.write_log(f"could not validate contact as module package. KeyError")
      return
    self.answer_server(validated_request_package)
    return

  def answer_server(self, validated_request_package):
    """Contacts the server to send requested module values.

    Args:
      server_request: The complete data send by server with requested modules

    Returns:
      None in any case.
    """
    for module in validated_request_package.modules:
      module.get_information()
    self.write_log(f"answering server")
    server_response = requests.post(f"https://{self.config['serverurl']}/answer",
     json=validated_request_package.to_json(),
     verify=self.config["server_cert"])
    if server_response.status_code != 200:
      self.write_log(f"server answerer with status code {server_response.status_code}")
      return
    self.write_log(f"communication successful!")

  ### BOILERPLATE

  def __init__(self, config_path = "cfg/client_config.yml"):
    self.carter_type = "client"
    self.config_path = config_path
    self.config = self.get_config()
    self.version = "0.1"
    self.fqdn = socket.getfqdn()
    print(self.config)
