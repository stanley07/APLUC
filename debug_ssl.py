import ssl
import socket
import logging
import os

# Configure logging
logging.basicConfig(filename='ssl_debug.log', level=logging.DEBUG)

# Set SSLKEYLOGFILE environment variable
os.environ['SSLKEYLOGFILE'] = 'ssl_keys.log'

def debug_ssl(hostname, port):
    # Create SSL context
    context = ssl.create_default_context()
    context.set_ciphers('DEFAULT@SECLEVEL=1')  # Adjust cipher suite if needed

    try:
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=hostname)
        conn.connect((hostname, port))

        # Log SSL/TLS version and cipher information
        logging.debug("SSL/TLS Version: %s", conn.version())
        logging.debug("Cipher: %s", conn.cipher())

        # Retrieve and log the server's certificate
        cert = conn.getpeercert()
        logging.debug("Server Certificate: %s", cert)

    except Exception as e:
        logging.error("Error occurred: %s", e)

    finally:
        if conn:
            # Close the connection
            conn.close()

if __name__ == "__main__":
    hostname = '127.0.0.1'  # Change to your server's hostname
    port = 443  # Change to your server's port number
    debug_ssl(hostname, port)
