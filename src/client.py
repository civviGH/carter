from src.core import CarterCore
from flask import Flask, request, abort, jsonify
import json
from src.exceptions import *
import psutil

class CarterClient(CarterCore):

  def setup_flask_routing(self):
    @self.flask_app.route("/")
    def index():
      return "hi"

    @self.flask_app.route("/poll", methods = ["POST"])
    def handle_poll():
      self.write_log(f"handling poll request from {request.remote_addr}")
      try:
        validated_post = self.validate_request_protocol(json.loads(request.json))
      except InvalidProtocol as ip:
        response = jsonify(ip.to_dict())
        response.status_code = 400
        return response

      response = self.forge_answer_payload()
      for module in validated_post["requested"]:
        module_answer = {}
        module_answer["name"] = module["name"]
        try:
          module_answer["value"] = self.get_module_output(module["name"])
        except UnknownModule as um:
          response = jsonify(um.to_dict())
          response.status_code = 400
          return response
        response["answers"].append(module_answer)
      return jsonify(response), 200

  def get_module_output(self, modulename):
    if modulename == "cpu_load":
      return psutil.cpu_percent()
    raise UnknownModule()

  def forge_answer_payload(self):
    payload = {}
    payload["type"] = "answer"
    payload["answers"] = []
    payload["version"] = self.version
    return payload

  def run(self):
    self.setup_flask_routing()
    self.flask_app.run(debug=True, ssl_context="adhoc")

  def __init__(self, config_path = "cfg/client_config.yml"):
    self.carter_type = "client"
    self.config_path = config_path
    self.config = self.get_config()
    self.version = "0.1"
    if self.config is None:
      self.write_log(f"{self.config_path} could not be read.")
    self.flask_app = Flask(__name__)
