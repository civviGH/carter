from OpenSSL import crypto, SSL
from socket import gethostname
from time import gmtime, mktime

from datetime import datetime, timedelta

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

def create_cert(CERT_FILE = "temp/selfsigned.crt", KEY_FILE = "temp/private.key"):
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

  subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"DE"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Bonn"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Bonn"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"CARTER"),
    x509.NameAttribute(NameOID.COMMON_NAME, gethostname()),
  ])

  cert_builder = x509.CertificateBuilder(
    issuer_name=issuer,
    subject_name=issuer,
    public_key=key.public_key(),
    serial_number=x509.random_serial_number(),
    not_valid_before=datetime.utcnow(),
    not_valid_after=datetime.utcnow() + timedelta(days=10)
  )

  cert = cert_builder.sign(key, hashes.SHA256(), default_backend())

  with open(CERT_FILE, "wb") as cf:
    cf.write(cert.public_bytes(serialization.Encoding.PEM))

def create_self_signed_certificate(CERT_FILE = "temp/selfsigned.crt", KEY_FILE = "temp/private.key"):
  """Creates and saves a self signed certificate.

  Args:
    CERT_FILE: filename to save the certificate in.
    KEY_FILE: filename to save the private key in.

  Returns:
    (CERT_FILE, KEY_FILE) on success, None otherwise.

  Todo:
    Allow customization of the Certificate inputs like ``C`` and ``ST``.
  """
  k = crypto.PKey()
  k.generate_key(crypto.TYPE_RSA, 1024)

  cert = crypto.X509()
  cert.get_subject().C = "DE"
  cert.get_subject().ST = "Bonn"
  cert.get_subject().L = "Bonn"
  cert.get_subject().O = "CARTER"
  cert.get_subject().OU = "CARTER"
  cert.get_subject().CN = gethostname()
  cert.set_serial_number(1000)
  cert.gmtime_adj_notBefore(0)
  # YEARS*DAYS*HOURS*MINUTES*SECONDS
  cert.gmtime_adj_notAfter(10*365*24*60*60)
  cert.set_issuer(cert.get_subject())
  cert.set_pubkey(k)

  with open(CERT_FILE, "wb") as cf:
    cf.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
  with open(KEY_FILE, "wb") as kf:
    kf.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
  return (CERT_FILE, KEY_FILE)

if __name__ == "__main__":
  #create_self_signed_certificate()
  create_cert()
