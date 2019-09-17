from OpenSSL import crypto, SSL
from socket import gethostname
from time import gmtime, mktime

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

if __name__ == "__main__":
  create_self_signed_certificate()
