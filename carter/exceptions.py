class CarterBaseException(Exception):
  def __init__(self, message):
    Exception.__init__(self)
    self.message = message

  def to_dict(self):
    rv = {}
    rv["message"] = self.message
    return rv

class InvalidProtocol(CarterBaseException):
  def __init__(self, message = "invalid CARTER protocol format"):
    CarterBaseException.__init__(self, message)

class UnknownModule(CarterBaseException):
  def __init__(self, message = "unknown module requested"):
    CarterBaseException.__init__(self, message)

class ConfigNotFound(CarterBaseException):
  def __init__(self, message = "no config file found"):
    CarterBaseException.__init__(self, message)

class ConfigUnreadable(CarterBaseException):
  def __init__(self, message = "config file is no valid yaml"):
    CarterBaseException.__init__(self, message)
