import yaml
import datetime
import os
from carter.exceptions import *

class CarterCore:

  def write_log(self, message):
    # placeholder logging, just print to console
    datetime_object = datetime.datetime.now()
    print(f"[{datetime_object}] [{self.carter_type}] - {message}")

  def get_config(self):
    config = self.get_dict_from_yaml_filename(self.config_path)
    return config

  def get_dict_from_yaml_filename(self, filename):
    if not os.path.isfile(filename):
      self.write_log(f"{filename} file not found")
      raise ConfigNotFound()
    with open(filename, "r") as file_descriptor:
      try:
        output = yaml.safe_load(file_descriptor)
      except yaml.scanner.ScannerError as yaml_error:
        self.write_log(f"file {file_descriptor.name} is no valid yaml.")
        raise ConfigUnreadable()
    return output

  def validate_and_return_request_protocol(self, protocol_dict):
    if not all(k in protocol_dict for k in ("type","version","requested")):
      raise InvalidProtocol("Not all needed keys found in protocol")
    if protocol_dict["type"] != "request":
      raise InvalidProtocol(f"Wrong protocol type for {self.carter_type}")
    if protocol_dict["version"] != self.version:
      raise InvalidProtocol(f"Version missmatch: I am {self.version}, but the protocol speaks {protocol_dict['version']}")
    if len(protocol_dict["requested"]) <= 0:
      raise InvalidProtocol(f"No modules requested")
    return protocol_dict

  def validate_and_return_answer_protocol(self, protocol_dict):
    if not all(k in protocol_dict for k in ("type","version","answers")):
      raise InvalidProtocol("Not all needed keys found in protocol")
    if protocol_dict["type"] != "answer":
      raise InvalidProtocol(f"Wrong protocol type for {self.carter_type}")
    if protocol_dict["version"] != self.version:
      raise InvalidProtocol(f"Version missmatch: I am {self.version}, but the protocol speaks {protocol_dict['version']}")
    if len(protocol_dict["answers"]) <= 0:
      raise InvalidProtocol(f"No answers received")
    return protocol_dict

  def validate_and_return_contact_protocol(self, protocol_dict):
    if not all(k in protocol_dict for k in ("type","version")):
      raise InvalidProtocol("Not all needed keys found in protocol")
    if protocol_dict["type"] != "helo":
      raise InvalidProtocol(f"Wrong protocol type for {self.carter_type}")
    if protocol_dict["version"] != self.version:
      raise InvalidProtocol(f"Version missmatch: I am {self.version}, but the protocol speaks {protocol_dict['version']}")
    return protocol_dict
