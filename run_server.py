from django.core.management import execute_from_command_line
from django.conf import settings
import os

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apluc.settings')

if __name__ == "__main__":
    # Check if SSL certificate and key files exist
    cert_file = 'cert.pem'
    key_file = 'key.pem'
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("Error: SSL certificate or key file not found.")
        exit(1)

    # Update Django settings to use SSL
    settings.RUNSERVER_PLUS_SERVER_ADDRESS_PORT = '0.0.0.0:443'
    settings.RUNSERVER_PLUS_USE_SSL = True
    settings.RUNSERVER_PLUS_CERT_FILE = cert_file
    settings.RUNSERVER_PLUS_KEY_FILE = key_file

    # Start the development server with SSL
    execute_from_command_line(['manage.py', 'runserver_plus', '--cert-file', cert_file, '--key-file', key_file])
