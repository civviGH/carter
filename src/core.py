import yaml
import datetime
import os
from src.exceptions import *

class CarterCore:

  def write_log(self, message):
    # placeholder logging, just print to console
    datetime_object = datetime.datetime.now()
    print(f"[{datetime_object}] [{self.carter_type}] - {message}")

  def get_config(self):
    config = self.get_dict_from_yaml_filename(self.config_path)
    return config

  def get_dict_from_yaml_filename(self, filename):
    output = None
    if not os.path.isfile(filename):
      return output
    with open(filename, "r") as file_descriptor:
      try:
        output = yaml.safe_load(file_descriptor)
      except yaml.scanner.ScannerError as yaml_error:
        self.write_log(f"yaml file {file_descriptor.name} is no valid yaml.")
    return output

  def validate_request_protocol(self, dict):
    if not all(k in dict for k in ("type","version","requested")):
      raise InvalidProtocol("Not all needed keys found in protocol")
    if dict["type"] != "request":
      raise InvalidProtocol(f"Wrong protocol type for {self.carter_type}")
    if dict["version"] != self.version:
      raise InvalidProtocol(f"Version missmatch: I am {self.version}, but the protocol speaks {dict['version']}")
    if len(dict["requested"]) <= 0:
      raise InvalidProtocol(f"No modules requested")
    return dict

  def validate_answer_protocol(self, dict):
    if not all(k in dict for k in ("type","version","answers")):
      raise InvalidProtocol("Not all needed keys found in protocol")
    if dict["type"] != "answer":
      raise InvalidProtocol(f"Wrong protocol type for {self.carter_type}")
    if dict["version"] != self.version:
      raise InvalidProtocol(f"Version missmatch: I am {self.version}, but the protocol speaks {dict['version']}")
    if len(dict["answers"]) <= 0:
      raise InvalidProtocol(f"No answers received")
    return dict