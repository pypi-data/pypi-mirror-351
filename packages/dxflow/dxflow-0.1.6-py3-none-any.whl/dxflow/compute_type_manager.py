import requests
import json

from .api_tools import make_api_request
from .utils import print_table

class ComputeTypeManager:
    """
    A class that manages compute types for a given namespace.

    Args:
        namespace_pointer (str): The pointer to the namespace.
        namespace_secret (str): The secret key for the namespace.
        provider (str): The provider for the compute types. Default is "AWS".
        namespace_name (str): The name of the namespace. Default is "diphyx".
        api_url (str): The URL of the API.

    Attributes:
        namespace_pointer (str): The pointer to the namespace.
        namespace_name (str): The name of the namespace.
        namespace_secret (str): The secret key for the namespace.
        api_url (str): The URL of the API.
        provider (str): The provider for the compute types.
    """

    def __init__(self, namespace_pointer=None, namespace_secret=None, provider="AWS", namespace_name="diphyx", api_url=None):
        self.namespace_pointer = namespace_pointer
        self.namespace_name = namespace_name
        self.namespace_secret = namespace_secret
        self.api_url = api_url
        self.provider= provider

    def create(self, provider="AWS", name=None, type=None, os="LINUX", arch="AMD64", cpu: int=None, memory: int=None, disk_size:int =16, machine_price=None, disk_price =None, image_id=None, tags=None):
        """
        Creates a new compute type.

        Args:
            provider (str): The provider for the compute type. Default is "AWS".
            name (str): The name of the compute type.
            type (str): The type of the compute type.
            os (str): The operating system of the compute type. Default is "LINUX".
            arch (str): The architecture of the compute type. Default is "AMD64".
            cpu (int): The number of CPUs for the compute type.
            memory (int): The amount of memory in GB for the compute type.
            disk_size (int): The size of the native disk in GB. Default is 16.
            machine_price (float): The price of the machine.
            disk_price (float): The price of the disk.
            image_id (str): The ID of the image.
            tags (list): The tags for the compute type.

        Returns:
            dict: The response from the API.
        """
        url = f"{self.api_url}/namespaces/{self.namespace_pointer}/compute/types/"
        body = {
            "provider": provider,
            "name": name.title().replace(".", " "),
            "os": os,
            "arch": arch,
            "cpu": int(cpu),
            "memory": int(memory),
            "disk": disk_size,
            "price": {
                "machine": machine_price,
                "disk": disk_price if disk_price is not None else self._disk_price(provider)
            },
            "resources": {
                "type": type,
                "image": image_id if image_id is not None else self._get_image_id(provider, os, arch)
            },
            "tags": tags if tags is not None else (["EBS"] if provider == "AWS" else None)
        }

        headers = {"X-SECRET-KEY": self.namespace_secret}
        response = make_api_request(url, headers=headers, json=body, method='POST')
        return response

    def list(self, filters=None, table=True):
        """
        Lists all compute types for the namespace.

        Args:
            filters (dict): Filters to apply to the list. Default is None.
            table (bool): Whether to display the list as a table. Default is True.
        """
        url = f"{self.api_url}/namespaces/{self.namespace_pointer}/compute/types/"
        headers = {"X-SECRET-KEY": self.namespace_secret}
        compute_types = make_api_request(url=url, headers=headers, method='GET')
        compute_types = compute_types["list"]

        if table:
            table_headers = ["Name", "Pointer", "Provider", "Type" , "OS", "Architecture", "CPU", "Memory", "Native Disk", "Machine Price", "Disk Price"]
            compute_data = []
            for compute_type in compute_types:
                compute_row = {
                    "Name": compute_type.get("name"),
                    "Pointer": compute_type.get("pointer"),
                    "Provider": compute_type.get("provider"),
                    "Type": compute_type.get("resources").get("type"),
                    "OS": compute_type.get("os"),
                    "Architecture": compute_type.get("arch"),
                    "CPU": compute_type.get("cpu"),
                    "Memory": compute_type.get("memory"),
                    "Native Disk": compute_type.get("disk"),
                    "Machine Price": compute_type.get("price").get("machine"),
                    "Disk Price": compute_type.get("price").get("disk")
                }
                compute_data.append(compute_row)

            print_table(compute_data, table_headers)
        else:
            print(json.dumps(compute_types, indent=4))

        return compute_types
    
    def get_unit(self, name=None, ip_address=None):
        """
        Gets the unit for the given name or IP address.

        Args:
            name (str): The name of the unit. Default is None.
            ip_address (str): The IP address of the unit. Default is None.
        """
        pass

    def _disk_price(self, provider):
        """
        Returns the price of the disk for the given provider.

        Args:
            provider (str): The provider.

        Returns:
            float: The price of the disk.
        """
        if provider == "AWS":
            return 0.085
        elif provider == "GCP":
            return 0.65
        elif provider == "Azure":
            return 0.085
        else:
            return 0.085

    def _get_image_id(self, provider, os, arch):
        """
        Returns the image ID for the given provider, operating system, and architecture.

        Args:
            provider (str): The provider.
            os (str): The operating system.
            arch (str): The architecture.

        Returns:
            str: The image ID.
        """
        if provider == "AWS":
            if os == "LINUX":
                if arch == "AMD64":
                    return "ami-0c7217cdde317cfec"
                elif arch == "ARM64":
                    return "ami-05d47d29a4c2d19e1"
        elif provider == "GCP":
            if os == "LINUX":
                if arch=="AMD64":
                    return "projects/ubuntu-os-cloud/global/images/ubuntu-minimal-2004-focal-v20231213a"
                elif arch=="ARM64":
                    return "projects/ubuntu-os-cloud/global/images/ubuntu-minimal-2004-focal-arm64-v20231213a"
        elif provider == "Azure":
            return None
        else:
            return None