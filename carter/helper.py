from socket import getfqdn
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID

import json

def create_cert(CERT_FILE = "temp/cert.pem", KEY_FILE = "temp/private_key.pem"):
  key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
  )
  with open(KEY_FILE, "wb") as kf:
    kf.write(key.private_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PrivateFormat.TraditionalOpenSSL,
      encryption_algorithm=serialization.NoEncryption()
      ))

  san_list = [x509.DNSName(u"{}".format(getfqdn()))]

  subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"DE"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Bonn"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Bonn"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"CARTER"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"{}".format(getfqdn()))
  ])

  cert_builder = x509.CertificateBuilder(
    issuer_name=issuer,
    subject_name=subject,
    public_key=key.public_key(),
    serial_number=x509.random_serial_number(),
    not_valid_before=datetime.utcnow(),
    not_valid_after=datetime.utcnow() + timedelta(days=10)
  )

  cert_builder = cert_builder.add_extension(
    x509.SubjectAlternativeName(san_list),
    critical=False
  )

  cert = cert_builder.sign(key, hashes.SHA256(), default_backend())

  with open(CERT_FILE, "wb") as cf:
    cf.write(cert.public_bytes(serialization.Encoding.PEM))

def get_default_render_options():
  render_options = {}
  render_options["type"] = "bar"
  render_options["data"] = {}
  render_options["data"]["datasets"] = []
  render_options["options"] = {}
  render_options["options"]["scales"] = {}
  render_options["options"]["scales"]["yAxes"] = []
  yAxes = {}
  yAxes["ticks"] = {}
  yAxes["ticks"]["beginAtZero"] = True
  yAxes["ticks"]["max"] = 100
  render_options["options"]["scales"]["yAxes"].append(yAxes)
  render_options["options"]["responsive"] = False
  render_options["options"]["animation"] = False
  return render_options

if __name__ == "__main__":
  create_cert()
