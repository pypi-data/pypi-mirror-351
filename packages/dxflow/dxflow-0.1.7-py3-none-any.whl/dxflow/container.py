import requests
import json
import time


from dxflow.utils import Status
from .utils import log_viewer, CommandStatus

class UnitContainersManager:
    def __init__(self, unit_secret=None, dxflow_url=None):
        """
        Initializes a UnitContainers object.

        Args:
            unit_secret (str): The secret key for authentication.
            dxflow_url (str): The URL of the DxFlow server.
        """
        self._unit_secret = unit_secret
        self.dxflow_url = dxflow_url
        self.containers_info = None
        self.list(print_info=False) # Fetches the list of containers
        if self.containers_info is not None:
            self.containers = [self._assign_container(container_info) for container_info in self.containers_info]
        else:
            self.containers = []

    def list(self, print_info=True):
        """
        Lists all containers.

        Returns:
            If the request is successful (status code 200), the JSON response is returned.
            Otherwise, a tuple containing the status code and the response text is returned.
        """
        url = f'{self.dxflow_url}/api/containers/'
        headers = {"X-SECRET-KEY": self._unit_secret}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.containers_info = response.json()
            if print_info:
                print(json.dumps(self.containers_info, indent=4))
            return response.json()
        else:
            return response.status_code, response.text    
    
    def _assign_container(self, container_info):
        return Container(project = container_info.get("project") if container_info else None,
                        container_id=container_info.get("id") if container_info else None,
                        name = container_info.get("name") if container_info else None,
                        status = Status.from_string(container_info.get("status")) if container_info else None,
                        date = container_info.get("date") if container_info else None,
                        image = container_info.get("image") if container_info else None,
                        entrypoint = container_info.get("entrypoint") if container_info else None,
                        command = container_info.get("command") if container_info else None,
                        volumes = container_info.get("volumes") if container_info else None,
                        ports = container_info.get("ports") if container_info else None,
                        environments = container_info.get("environments") if container_info else None,
                        unit_secret=self._unit_secret, 
                        dxflow_url=self.dxflow_url)
        

class Container:
    def __init__(self, project=None, container_id=None, name=None, status=None, date=None, image=None, entrypoint=None, command=None, volumes=None, ports=None, environments=None, unit_secret=None, dxflow_url=None):
        """
        Initializes a Container object.

        Args:
            container_id (str): The ID of the container.
            unit_secret (str): The secret key for authentication.
            dxflow_url (str): The URL of the DxFlow server.
        """
        self.container_id = container_id
        self.name = name
        self.status = status
        self.date = date
        self.image = image
        self.entrypoint = entrypoint
        self.command = command
        self.volumes = volumes
        self.ports = ports
        self.environments = environments
        self._unit_secret = unit_secret
        self.dxflow_url = dxflow_url
        self.project = project if project else None


    def __str__(self):
        return f"{{'name': {self.name}, 'container_id': {self.container_id}, 'status': {self.status}}}"
        
    def detail(self, print_info=True):
        """
        Fetches details of the container.
        Read this for more information: https://github.com/diphyx/dxf/blob/main/core/api/bruno/requests/container/get-list.bru

        Returns:
            If the request is successful (status code 200), the JSON response is returned.
            Otherwise, a tuple containing the status code and the response text is returned.
        """
        url = f'{self.dxflow_url}/api/containers/{self.container_id}/'
        headers = {"X-SECRET-KEY": self._unit_secret}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.container_info = response.json()
            self.status = Status.from_string(self.container_info.get("status"))
            if print_info:
                print(json.dumps(self.container_info, indent=4))
            return self.container_info
        else:
            return response.status_code, response.text
        

    def logs(self, print_info=True):
        """
        Fetches the logs of the container.
        Read this for more information: https://github.com/diphyx/dxf/blob/main/core/api/bruno/requests/container/get-logs.bru

        Args:
            print_info (bool): Whether to print the logs information.

        Returns:
            If the request is successful (status code 200), the JSON response is returned.
            Otherwise, a tuple containing the status code and the response text is returned.
        """
        url = f'{self.dxflow_url}/api/containers/{self.container_id}/logs/'
        headers = {"X-SECRET-KEY": self._unit_secret}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self._logs = response.json()
            if print_info:
                log_viewer(self._logs)
            return self._logs
        else:
            raise Exception(f"Failed to fetch logs: {response.status_code}, {response.text}")   
            

    def events(self, print_info=True):
       # https://github.com/diphyx/dxf/blob/main/core/api/bruno/requests/container/get-events.bru
        url = f'{self.dxflow_url}/api/containers/{self.container_id}/events/'
        headers = {"X-SECRET-KEY": self._unit_secret}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.events = response.json()
            if print_info:
                print(json.dumps(self.events, indent=4))
            return self.events
        else:
            return response.status_code, response.text

    def change_status(self, status: CommandStatus):
        if status == CommandStatus.UNKNOWN or status not in [CommandStatus.START, CommandStatus.STOP, CommandStatus.PAUSE, CommandStatus.UNPAUSE, CommandStatus.TERMINATE]:
            print(f"Unknown or unsupported command: {status}")
            return None
        
        current_status = self.get_status()
        
        if  (current_status == Status.TERMINATED) or \
            (current_status == Status.PAUSED and status == CommandStatus.PAUSE) or \
            (current_status == Status.RUNNING and status == CommandStatus.START) or \
            (current_status == Status.STOPPED and status == CommandStatus.STOP): 
            print(f"Container is already {current_status.name}, command to {status.name} is omitted")
            return None
        
        if current_status == Status.PAUSED and status == CommandStatus.START:
            print(f"ERROR: Cannot Start the paused {self.name} container, you an uunpause it: by container.unpause()")
            return None
        
        url = f'{self.dxflow_url}/api/containers/{self.container_id}/{status.value.lower()}/'
        headers = {"X-SECRET-KEY": self._unit_secret}
        response = requests.put(url, headers=headers)
        if response.status_code == 200: ## bg: check if the status is changed to the new one - 202
            return "Container started successfully"
        else:
            raise Exception(f"Failed to change status to {status.value}: {response.status_code}, {response.text}")

    def start(self):
        """
        Starts the container.
        """
        return self.change_status(CommandStatus.START)

    def stop(self):
        """
        Stops the container.
        """
        return self.change_status(CommandStatus.STOP)
        
    def pause(self):
        """
        Pauses the container.
        """
        return self.change_status(CommandStatus.PAUSE)
    
    def unpause(self):
        """
        Unpauses the container.
        """
        return self.change_status(CommandStatus.UNPAUSE)
    
    def terminate(self):
        """
        Terminates the container.
        """
        return self.change_status(CommandStatus.TERMINATE)
    
    def status_watcher(self, status=Status.COMPLETED, timeout=600, poll_interval=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_status = self.get_status()
            ## bg: if the the container Failes or return error then it never get to the state of COMPLETED! - Fix this ???
            if current_status == status:
                return True
            time.sleep(poll_interval)
        return False

    def get_status(self):
        self.detail(print_info=False)
        return self.status
    
    def get_stats(self, print_info=True, limit=1, query_type="LAST", duration=60000, resources="cpu,memory"):
        """
        Fetches the stats of the container.
        Read this for more information: https://github.com/diphyx/dxf/blob/main/core/api/bruno/requests/container/get-stats.bru

        Args:
            print_info (bool): Whether to print the stats information.
            limit (int): The number of stats entries to fetch.
            query_type (str): The type of query (e.g., "LAST").
            duration (int): The duration in milliseconds for which stats are fetched.
            resources (str): The resources to include in the stats (e.g., "cpu,memory").

        Returns:
            If the request is successful (status code 200), the JSON response is returned.
            Otherwise, a tuple containing the status code and the response text is returned.
        """
        url = f'{self.dxflow_url}/api/containers/{self.container_id}/stats/'
        headers = {"X-SECRET-KEY": self._unit_secret}
        params = {
            "limit": limit,
            "type": query_type,
            "duration": duration,
            "resources": resources
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            self.stats = response.json()
            if print_info:
                print(json.dumps(self.stats, indent=4))
            return self.stats
        else:
            return response.status_code, response.text
