from .authentication import SecretsManager, authenticate_user
from .storage import StorageManager
from .compute import ComputeManager
from .flow import FlowRegisteryManager

from .compute_type_manager import ComputeTypeManager

from .config import NAMESPACE_API_URL
class Session:
    """
    Represents a session for managing compute, storage, flow, and compute types.

    Args:
        secrets (dict, optional): A dictionary containing user and namespace secrets. Defaults to None.
        email (str, optional): The email address of the user. Required if `password` is provided. Defaults to None.
        password (str, optional): The password of the user. Required if `email` is provided. Defaults to None.
    """

    def __init__(self, secrets=None, email=None, password=None, namespace='diphyx'):
        """
        Initializes a new instance of the Session class.

        If `email` and `password` are provided, the user will be authenticated using the provided credentials.
        If `secrets` is not provided, the secrets will be loaded from the secret manager.

        Args:
            secrets (dict, optional): A dictionary containing user and namespace secrets. Defaults to None.
            email (str, optional): The email address of the user. Required if `password` is provided. Defaults to None.
            password (str, optional): The password of the user. Required if `email` is provided. Defaults to None.
        """
        if namespace.lower() == 'diphyx':
            self.namespace = 'diphyx'
        else:
            self.namespace = namespace
        
        if (email is not None) and (password is not None):
            self.secrets = authenticate_user(email=email, password=password, namespace=self.namespace)

        elif secrets is None:
            self.secret_manager=SecretsManager()
            self.secrets = self.secret_manager.load_secrets()

        self.namespace_api_url = NAMESPACE_API_URL

    def get_compute_manager(self):
        """
        Gets an instance of the ComputeManager class.

        Returns:
            ComputeManager: An instance of the ComputeManager class.
        """
        return ComputeManager(user_pointer=self.secrets["user"]["pointer"],
                              user_secret=self.secrets["user"]["secret"],
                              namespace_pointer=self.secrets["namespace"]["pointer"],
                              namespace_secret=self.secrets["namespace"]["secret"])

    def get_storage_manager(self):
        """
        Gets an instance of the StorageManager class.

        Returns:
            StorageManager: An instance of the StorageManager class.
        """
        return StorageManager(user_pointer=self.secrets["user"]["pointer"],
                              user_secret=self.secrets["user"]["secret"])
    
    def get_flow_registery_manager(self, api_url=NAMESPACE_API_URL):
        """
        Gets an instance of the FlowRegisteryManager class.

        Args:
            api_url (str, optional): The API URL for the namespace. Defaults to http://diphyx.com

        Returns:
            FlowRegisteryManager: An instance of the FlowRegisteryManager class.
        """
        return FlowRegisteryManager(namespace_pointer=self.secrets["namespace"]["pointer"],
                              namespace_secret=self.secrets["namespace"]["secret"],
                              api_url=NAMESPACE_API_URL)
    
    def get_compute_type_mananger(self):
        """
        Gets an instance of the ComputeTypeManager class.

        Returns:
            ComputeTypeManager: An instance of the ComputeTypeManager class.
        """
        return ComputeTypeManager(namespace_pointer=self.secrets["namespace"]["pointer"],
                            namespace_secret=self.secrets["namespace"]["secret"],
                            api_url=NAMESPACE_API_URL)  
    