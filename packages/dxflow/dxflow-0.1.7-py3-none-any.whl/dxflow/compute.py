import requests
import json
import datetime
import os
import socket

from .config import NAMESPACE_API_URL
from .utils.file_utils import list_files
from .utils import print_table
from .storage import UnitStorage
from .container import UnitContainersManager
from .project import UnitProjectsManager
from .utils import Status


class ComputeManager:
    """
    A class that manages compute units.

    Attributes:
        user_pointer (str): The user pointer.
        user_secret (str): The user secret.
        api_url (str): The API URL.
        content (dict): The content.
        compute_units_info (dict): The compute units information.
        compute_units (dict): The compute units.

    Methods:
        update_list: Updates the list of compute units.
        get_unit: Retrieves a compute unit by name or IP address.
        _assing_compute_units: Assigns compute units.
        list: Lists the compute units.
    """

    def __init__(self, user_pointer=None, user_secret=None, namespace_pointer=None, namespace_secret=None, api_url=NAMESPACE_API_URL):
        """
        Initializes a new instance of the ComputeManager class.

        Args:
            user_pointer (str, optional): The user pointer. Defaults to None.
            user_secret (str, optional): The user secret. Defaults to None.
            api_url (str, optional): The API URL. Defaults to NAMESPACE_API_URL.
        """
        self.user_pointer = user_pointer
        self._user_secret = user_secret
        self.namespace_pointer = namespace_pointer
        self._namespace_secret = namespace_secret
        self.api_url = api_url
        self.content = {}
        self.compute_units_info = None
        self.compute_units = {}


    def update_list(self, namespace='diphyx', status=None, name=None):
        """
        Updates the list of compute units.

        Args:
            namespace (str, optional): The namespace. Defaults to 'diphyx'.
            status (str, optional): The status. Defaults to None.
            name (str, optional): The name. Defaults to None.

        Returns:
            dict or tuple: The content or the status code and response text.
        """
        # Construct the base URL
        url = f'{self.api_url}/users/{self.user_pointer}/compute/units/'
        headers = {"X-SECRET-KEY": self._user_secret }

        # Prepare the parameters for filtering
        params = {}
        if status:
            params['status'] = status
        if name:
            params['name'] = name

        # Make the GET request with optional filters
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                content = response.json()

                self.compute_units_info = content
                for unit in self.compute_units_info['list']:
                    self.compute_units[unit['name']] = self._assing_compute_units(unit)
                return content
            else:
                print(response.status_code, response.text)
                return response.status_code, response.text
        except Exception as e:
            # Handle the exception
            return str(e)

    def get_unit(self, name: str = None, ip_address: str = None) -> 'ComputeUnit':
        """
        Retrieves a compute unit by name or IP address.

        Args:
            name (str, optional): The name. Defaults to None.
            ip_address (str, optional): The IP address. Defaults to None.

        Returns:
            ComputeUnit or None: The compute unit or None if not found.
        
        Raises:
            ValueError: If no compute unit matches both provided name and IP address.
        """
        if self.compute_units=={}:
            self.update_list()  ## dxa: we shoud not update the whole list for one compute unit.

        if name and ip_address:
            # Check if both name and IP address match the same unit
            for unit in self.compute_units_info['list']:
                if unit['name'] == name and unit['ip'] == ip_address:
                    return self._assing_compute_units(unit, True)
            raise ValueError("No compute unit matches both provided name and IP address")

        elif ip_address:
            for unit in self.compute_units_info['list']:
                if unit['ip'] == ip_address:
                    return self._assing_compute_units(unit, True)
            raise ValueError(f"No compute unit found with the provided IP address={ip_address}")
        
        elif name:
            for unit in self.compute_units_info['list']:
                if unit['name'] == name:
                    return self._assing_compute_units(unit, True)
            raise ValueError(f"No compute unit found with the provided name={name}")
        
        elif not name and not ip_address:
            # Get the IP address of the current machine
            current_ip = get_ip_address_of_current_machine()
            for unit in self.compute_units_info['list']:
                if unit['ip'] == current_ip:
                    return self._assing_compute_units(unit, True)
            raise ValueError(f"No compute_name or IP address provided. No compute unit found with the current machine's IP address={current_ip}")    

        raise ValueError("No compute unit found with the provided name or IP address")       

    def _assing_compute_units(self, unit_info, initialize_tools=False) -> 'ComputeUnit':
        """
        Assigns compute units.

        Args:
            unit_info (dict): The unit information.

        Returns:
            ComputeUnit: The compute unit.
        """
        return ComputeUnit(user_pointer=self.user_pointer, 
                           user_secret=self._user_secret, 
                           info=unit_info, 
                            namespace_pointer=self.namespace_pointer,
                           namespace_secret= self._namespace_secret, 
                           namespace_api_url=self.api_url,
                           initialize_tools=initialize_tools)


    def create(self, name, type_pointer, disk=10, 
               extensions=["proxy", "storage", "sync", "alarm"],
               protocol="HTTPS",
               secret="dxf-secret",
               ip="0.0.0.0"):
        
        url = f'{self.api_url}/users/{self.user_pointer}/compute/units/'
        headers = {"X-SECRET-KEY": self._user_secret}
        
        data = {
            "disk": disk,
            "extensions": extensions,
            "ip": ip,
            "name": name,
            "protocol": protocol,
            "secret": secret,
            "type": type_pointer
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            content = response.json()
            compute_unit = self._assing_compute_units(content, True)
            return compute_unit
        else:
            return response.status_code, response.text

    def list(self, table: bool = True, return_info: bool = False):
        """
        Lists the compute units.
        """
        # Define the header of the table
        self.update_list()
        if (not "list" in self.compute_units_info) or (self.compute_units_info["total"]==0):
            print("There is no compute-unit (in any status)")
            return "No compute units found."
        compute_units = self.compute_units_info.get("list")
        table_data =  show_compute_units(compute_units= compute_units, table=table)
        if return_info:
            return table_data


def show_compute_units(compute_units, table=True):
    """
    Displays the compute units information.

    Args:
        compute_units_info (dict): The compute units information.
        table (bool, optional): Whether to display as a table. Defaults to True.
    """
    table_headers = ["Name", "Status", "IP", "Cluster Type", "CPU", "Memory(GB)", "Disk"]


    # Iterate over each compute unit and print its details
    table_data = []
    for unit in compute_units:
        table_data.append({
            "Name": unit['name'],
            "Status": unit['status'],
            "IP": unit['ip'],
            "Cluster Type": f"{unit['type']['provider']}:{unit['type']['name']}",
            "CPU": unit['type']['cpu'],
            "Memory(GB)": unit['type']['memory'],
            "Disk": unit['type']['disk']
        }) 
    if table:
        print_table(table_data, table_headers)
    return table_data




class ComputeUnit:
    """
    A class that represents a compute unit.

    Attributes:
        user_pointer (str): The user pointer.
        user_secret (str): The user secret.
        info (dict): The unit information.
        namespace_api_url (str): The namespace API URL.
        content (dict): The content.
        compute_units_info (dict): The compute units information.
        _unit_secret (str): The unit secret.
        dxflow_url (str): The DXFlow URL.
        storage (UnitStorage): The unit storage.
        containers (UnitContainers): The unit containers.
        projects (UnitProjects): The unit projects.

    Methods:
        _get_secret: Retrieves the unit secret.
        get_secret: Retrieves the unit secret.
        detail: Retrieves the unit details.
        start: Starts the compute unit.
        stop: Stops the compute unit.
        troubleshoot: Troubleshoots the compute unit.
        terminate: Terminates the compute unit.
        stats: Retrieves the compute unit stats.
        _change_status: Changes the status of the compute unit.
    """

    def __init__(self, user_pointer, user_secret, info, namespace_pointer=None, namespace_secret=None, namespace_api_url=NAMESPACE_API_URL, initialize_tools=False):
        """
        Initializes a new instance of the ComputeUnit class.

        Args:
            user_pointer (str): The user pointer.
            user_secret (str): The user secret.
            info (dict): The unit information.
            namespace_api_url (str, optional): The namespace API URL. Defaults to NAMESPACE_API_URL.
        """
        self.user_pointer = user_pointer
        self._user_secret = user_secret
        self.info = info
        self._compute_pointer = info['pointer']
        self.namespace_pointer = namespace_pointer
        self._namespace_secret = namespace_secret
        self.namespace_api_url = namespace_api_url
        self.content = {}
        self.compute_units_info = None

        self._unit_secrets = info.get('secrets')
        # self._get_secret()
        self.dxflow_url = f"{info['protocol'].lower()}://{info['ip']}"

        self.name = info['name']
        self.storage = None
        self.containers = None
        self.projects = None

        if initialize_tools:
            self.initialize_storage()
            self.initialize_containers()
            self.initialize_projects()
    def initialize_storage(self):
        self.storage = UnitStorage(unit_secret=self._unit_secrets['RW'], dxflow_url=self.dxflow_url)
        return self.storage

    def initialize_containers(self):
        self.containers = UnitContainersManager(unit_secret=self._unit_secrets['RO'], dxflow_url=self.dxflow_url)
        return self.containers

    def initialize_projects(self):
        self.projects = UnitProjectsManager(unit_secrets=self._unit_secrets, namespace_pointer=self.namespace_pointer, namespace_secret=self._namespace_secret, dxflow_url=self.dxflow_url)
        return self.projects
    
    def __str__(self):
        return json.dumps(show_compute_units(compute_units=[self.info], table=False)[0], indent=4)

    def _get_secret(self):
        """
        Retrieves the unit secret.

        Returns:
            str or tuple: The unit secret or the status code and response text.
        """
        url = f'{self.namespace_api_url}/users/{self.user_pointer}/compute/units/{self._compute_pointer}/secret/'
        headers = {"X-SECRET-KEY": self._user_secret }
        # Make the GET request with optional filters
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            self.compute_units_info = content
            self._unit_secrets=content['secret']
            return self._unit_secrets
    
        else:
            # Handle errors or unsuccessful requests
            return response.status_code, response.text
        
    def get_secret(self):
        """
        Retrieves the unit secret.

        Returns:
            str or tuple: The unit secret or the status code and response text.
        """
        return self._get_secret
    
    def detail(self):
        """
        Retrieves the unit details.

        Returns:
            dict or tuple: The unit details or the status code and response text.
        """
        url = f'{self.namespace_api_url}/compute/units/{self._compute_pointer}/'
        headers = {"X-SECRET-KEY": self._unit_secrets }
        # Make the GET request with optional filters
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            self.details = content           
            return content
    
        else:
            # Handle errors or unsuccessful requests
            return response.status_code, response.text
    
    def start(self):
        """
        Starts the compute unit.

        Returns:
            dict or tuple: The response content or the status code and response text.
        """
        return self._change_status("start")

    def stop(self):
        """
        Stops the compute unit.

        Returns:
            dict or tuple: The response content or the status code and response text.
        """
        return self._change_status("stop")
        
    def troubleshoot(self):
        """
        Troubleshoots the compute unit.

        Returns:
            dict or tuple: The response content or the status code and response text.
        """
        return self._change_status("troubleshoot")
    
    def terminate(self):
        """
        Terminates the compute unit.

        Returns:
            dict or tuple: The response content or the status code and response text.
        """
        return self._change_status("terminate")
    
    def get_status(self):
        self.detail()
        return Status.from_string(self.details['status'])

    
    def stats(self):
        """
        Retrieves the compute unit stats.

        Returns:
            dict or tuple: The compute unit stats or the status code and response text.
        """
        url = f'{self.dxflow_url}/api/host/stats/'
        headers = {"X-SECRET-KEY": self._unit_secrets }
        
        # Make the GET request with optional filters
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()  
            return content
    
        else:
            # Handle errors or unsuccessful requests
            return response.status_code, response.text
        

    def _change_status(self,status):
        """
        Changes the status of the compute unit.

        Args:
            status (str): The status.

        Returns:
            dict or tuple: The response content or the status code and response text.
        """
        headers = {"X-SECRET-KEY": self._unit_secrets['RW'] }
        if status in ['start', 'stop', 'troubleshoot']:
            url = f'{self.namespace_api_url}/compute/units/{self._compute_pointer}/{status}/'
            response = requests.put(url, headers=headers)
        elif status == 'terminate':
            url = f'{self.namespace_api_url}/compute/units/{self._compute_pointer}/'
            response = requests.delete(url, headers=headers)

        if response.status_code == 200:
            content = response.json()         
            return content
    
        else:
            # Handle errors or unsuccessful requests
            return response.status_code, response.text
        


def get_ip_address_of_current_machine(dx_path=os.path.join("/volume",".dx")):
    """
    Returns the IP address of the current machine.
    """
    from pathlib import Path
    if os.path.exists(dx_path):
        latest_key = max(Path(os.path.join(dx_path, "ssl")).glob("*.key"), key=lambda p: p.stat().st_mtime, default=None)
        latest_key_name = latest_key.name.replace(".key", "")
        if latest_key is None:
            raise Exception("No key file found in the specified directory.")
        return latest_key_name