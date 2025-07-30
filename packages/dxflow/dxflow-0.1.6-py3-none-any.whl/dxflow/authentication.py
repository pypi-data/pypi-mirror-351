import requests
import yaml
import json
import os

from .config import NAMESPACE_API_URL, DXFLOW_FOLDER_NAME, SECRET_MANAGER
from .utils import make_containing_dirs


class SecretsManager:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SecretsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, secret_file_path=os.path.join(os.path.expanduser("~"), DXFLOW_FOLDER_NAME, "config.yaml")):
        self.secret_file_path = secret_file_path
        self.secrets = None

    def store_secrets(self, secrets):
        if ("namespace" in secrets) and ("user" in secrets):
            secrets_ ={}
            secrets_["diphyx-namespace-pointer"] = secrets["namespace"]["pointer"]
            secrets_["diphyx-namespace-secret"] = secrets["namespace"]["secret"]
            secrets_["diphyx-namespace-alias"] = secrets["namespace"].get("alias", "")
            secrets_["diphyx-user-pointer"] = secrets["user"]["pointer"]
            secrets_["diphyx-user-secret"] = secrets["user"]["secret"]
            secrets_["diphyx-user-email"] = secrets["user"].get("email", "")
        else:
            secrets_ = secrets

        make_containing_dirs(self.secret_file_path)
        with open(self.secret_file_path, 'w') as file:
            yaml.dump(secrets_, file, default_flow_style=False)
        
    def load_secrets(self):
        if not os.path.exists(self.secret_file_path):
            raise FileNotFoundError("Secrets file not found")

        with open(self.secret_file_path, 'r') as file:
            data = yaml.safe_load(file)

        self.secrets = {}
        self.secrets["namespace"] = {"pointer": data["diphyx-namespace-pointer"], "secret": data["diphyx-namespace-secret"], "alias": data["diphyx-namespace-alias"]}
        self.secrets["user"] = {"pointer": data["diphyx-user-pointer"], "secret": data["diphyx-user-secret"], "email": data["diphyx-user-email"]}
        return self.secrets

    def secrets_exist(self):
        return os.path.exists(self.secret_file_path)


if SECRET_MANAGER is None:
    SECRET_MANAGER = SecretsManager()

def authenticate_user(email, password, secret_manager=SECRET_MANAGER, namespace='diphyx', store_secrets=True):
    """
    Authenticate a user with DiPhyx platform.
    
    :param email: The email of the user
    :param password: The password of the user
    :param secret_manager: The SecretsManager instance to use for storing secrets
    :return: Authentication token or status
    """
    url = f'{NAMESPACE_API_URL}/secrets/'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "namespace": namespace,
        "email": email,
        "password": password
    }

    response = requests.put(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        # Assuming the API returns a token or similar success confirmation
        secrets=response.json()

        # Check for 'secret' and 'pointer' keys in both 'namespace' and 'user'
        if all(key in secrets.get('namespace', {}) for key in ['secret', 'pointer']) and \
           all(key in secrets.get('user', {}) for key in ['secret', 'pointer']):
            if store_secrets:
                secret_manager.store_secrets(secrets)  
            return secrets      
        else:
            return "Invalid response format", "Missing 'secret' or 'pointer' in response."
    else:
        # Handle errors or unsuccessful authentication attempts
        return response.status_code, response.text
    

