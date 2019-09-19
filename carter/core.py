import yaml
import datetime
import os
import json
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
    """Gets the dictionary from a file assuming yaml syntax.

    Args:
      filename: The path to the wanted file.

    Returns:
      The content of the file as a dictionary.

    Raises:
      carter.exceptions.ConfigNotFound: if the file does not exist.
      carter.exceptions.ConfigUnreadable: if the file is no valid yaml.
    """
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


class CarterPackage:

  def __init__(self, **kwargs):
    self.version = kwargs["version"]
    self.client_name = kwargs["client_name"]

  def to_json(self):
    return json.dumps(self, default=lambda o: getattr(o, '__dict__', str(o)))

class HelloPackage(CarterPackage):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

class ModulePackage(CarterPackage):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.token = kwargs["token"]
    self.modules = []
    if "modules" in kwargs:
      for module in kwargs["modules"]:
        if module["type"] == "cpu":
          self.modules.append(CPUModule(**module))
          continue
        if module["type"] == "memory":
          self.modules.append(MemoryModule(**module))
          continue
        raise UnknownModule(f"module with type {module['type']} unknown")

  def add_module(self, module):
    self.modules.append(module)

class CarterModule:

  def __init__(self, **kwargs):
    self.type = kwargs["type"]

  def init_render_options(self):
    render_options = {}
    render_options["data"] = {}
    return render_options

class CPUModule(CarterModule):

  def __init__(self, **kwargs):
    self.type = "cpu"
    self.label = "Cpu load"
    if "cpu_values" in kwargs:
      self.cpu_values = kwargs["cpu_values"]

  def get_information(self):
    import psutil
    self.cpu_values = psutil.cpu_percent(percpu=True)

  def __len__(self):
    try:
      return len(self.cpu_values)
    except:
      pass
    return 0

  def pp(self):
    return json.dumps(self.get_render_options(), sort_keys = True, indent = 2)

  def get_render_options(self):
    # proof of concept color coding
    DEFAULT_COLOR = "rgba(178, 178, 178, 0.2)"
    WARNING_COLOR = "rgba(234, 237, 37, 0.2)"
    ERROR_COLOR = "rgba(255, 99, 132, 0.2)"
    render_data = self.init_render_options()
    render_data["type"] = "bar"
    render_data["data"]["labels"] = list(range(1, len(self) + 1))
    dataset = {}
    dataset["label"] = self.label
    dataset["data"] = self.cpu_values
    dataset["backgroundColor"] = []
    for data in self.cpu_values:
      if data >= 80.0:
        dataset["backgroundColor"].append(ERROR_COLOR)
        continue
      if data >= 40.0:
        dataset["backgroundColor"].append(WARNING_COLOR)
        continue
      dataset["backgroundColor"].append(DEFAULT_COLOR)
    render_data["data"]["datasets"] = [dataset]
    return render_data

class MemoryModule(CarterModule):

  def __init__(self, **kwargs):
    self.type = "memory"
    self.label = "RAM usage"
    if "ram_values" in kwargs:
      self.ram_values = kwargs["ram_values"]

  def get_information(self):
    import psutil
    memory_values = psutil.virtual_memory()._asdict()
    total = memory_values['total']
    available = memory_values['available']
    rest = total - available
    self.ram_values = [total, available, rest]

  def __len__(self):
    try:
      return len(self.ram_values)
    except:
      pass
    return 0

  def pp(self):
    return json.dumps(self.get_render_options(), sort_keys = True, indent = 2)

  def get_render_options(self):
    USED_COLOR = "rgba(255, 99, 132, 0.2)"
    FREE_COLOR = "rgba(178, 178, 178, 0.2)"
    render_data = self.init_render_options()
    render_data["type"] = "doughnut"
    render_data["data"]["labels"] = ["free", "used"]
    dataset = {}
    dataset["label"] = self.label
    dataset["data"] = self.ram_values[1:]
    dataset["backgroundColor"] = [FREE_COLOR, USED_COLOR]
    render_data["data"]["datasets"] = [dataset]
    return render_data

class DiskModule(CarterModule):
  pass
