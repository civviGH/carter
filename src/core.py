import yaml
import datetime

class CarterCore():

  def write_log(message):
    # placeholder logging, just print to console
    datetime_object = datetime.datetime.now()
    print(f"[{datetime_object}] - {message}")

  def get_dict_from_yaml_file(file_descriptor):
    try:
      output = yaml.safe_load(file_descriptor)
    except yaml.scanner.ScannerError as yaml_error:
      CarterCore.write_log(f"yaml file {file_descriptor.name} is no valid yaml.")
      return None
    return output

  def get_string_from_yaml(yaml_string):
    return yaml.dump(yaml_string)

  def __init__(self):
    return
