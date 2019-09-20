from carter.core import *
from carter.exceptions import *
from flask import Flask, request
import json
import requests
import socket
import os


class CarterClient(CarterCore):

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

  def ask_for_server_certificate(self):
    server_response = requests.post(f"https://{self.config['serverurl']}/get_cert",
    json=json.dumps({"client_name": self.fqdn}),
    verify=False)
    if server_response.status_code != 200:
      self.write_log(f"server answerer with status code {server_response.status_code}")
      print(server_response.text)
      return
    self.write_log(f"retrieved server certificate, writing to {self.config['server_cert']}")
    with open(self.config["server_cert"], "w") as cert_file:
      cert_file.write(server_response.text)


  ### BOILERPLATE

  def run(self):
    if os.path.isfile(self.config["server_cert"]):
      self.write_log(f"found file {self.config['server_cert']}, contacting server")
      self.contact_server()
      return
    self.write_log(f"no file found at {self.config['server_cert']}, asking server for cert")
    self.ask_for_server_certificate()


  def __init__(self, config_path = "cfg/client_config.yml"):
    self.carter_type = "client"
    self.config_path = config_path
    self.config = self.get_config()
    self.version = "0.1"
    self.fqdn = socket.getfqdn()
    print(self.config)
