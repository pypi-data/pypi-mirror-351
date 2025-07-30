import requests
import json
import datetime
import yaml
from .config import NAMESPACE_API_URL
from .utils import print_table, Status, CommandStatus, log_viewer
from .container import Container
from .flow import FlowRegisteryManager, Flow
import time


class UnitProjectsManager:
    """
    A class that represents unit projects in the DXFlow SDK.
    """

    def __init__(self, unit_secrets=None, namespace_pointer=None, namespace_secret=None, dxflow_url=None):
        """
        Initializes a new instance of the UnitProjects class.

        Args:
            unit_secret (Optional): The unit secret for authentication.
            dxflow_url (Optional): The DXFlow URL.
        """
        self._unit_secrets = unit_secrets
        self.namespace_pointer = namespace_pointer
        self._namespace_secret = namespace_secret
        self.dxflow_url = dxflow_url
        self.projects = {}
        self.projects_info = None

    def update_list(self):
        """
        Retrieves a list of projects.

        Returns:
            If the request is successful, returns the list of projects as a JSON object.
            Otherwise, returns the status code and error message.
        """
        url = f'{self.dxflow_url}/api/projects/'
        headers = {"X-SECRET-KEY": self._unit_secrets['RO']}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.projects_info = response.json()
            for project_info in self.projects_info:
                self.projects[project_info["name"]] = self._assign_project(project_info)
        else:
            return response.status_code, response.text
    def list(self, update=True, return_info=False):
        if update or (self.projects_info is None):
            self.update_list()
        
        table_headers = ["Name","Creation date", "Status"]
        table_data = []
        for project_name in self.projects:
            project = self.projects[project_name]
            table_data.append({"Name": project.name, "Creation date": project.date, "Status": project.status()})

        print_table(table_data, table_headers)
        if return_info:
            return table_data


    def get(self, project_name):
        project_detail = self._get_detail(project_name)
        if isinstance(project_detail, tuple):
            print(f"Error retrieving project {project_name}: {project_detail[1]}")
            return None
        project = self._assign_project(project_detail)
        self.projects[project.name] = project
        
        return project
    def _get(self, project_name, update=True):
        if update or (self.projects_info is None):
            self.update_list()
        
        if project_name in self.projects:
            return self.projects[project_name]
        else:
            print(f"Project {project_name} not found")
            return None
  
    def _get_detail(self, project_name, update=True):
           
        url = f'{self.dxflow_url}/api/projects/{project_name}/'
        headers = {"X-SECRET-KEY": self._unit_secrets['RO']}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.text
    
    
    def create(self, flow_name: str, project_name: str=None, variables: dict=None) -> 'Project':
        """
        Creates a new project using a flow.

        Args:
            flow_name: The name of the flow to use for creating the project.
            project_name: The name of the project to create.
            variables: A dictionary of variables to replace in the flow template.

        Returns:
            If the request is successful, returns the created project as a JSON object.
            Otherwise, returns the status code and error message.
        """
        if (self.namespace_pointer is None) or (self._namespace_secret is None):
            raise ValueError("Namespace details are missing. Use create_from_comopse_yaml to create a project directly from a docker compose. Refer to the documentation for guidance.")
        flow = FlowRegisteryManager.get_by_flow_name(
            name=flow_name, 
            namespace_pointer=self.namespace_pointer, 
            namespace_secret=self._namespace_secret, 
            api_url=NAMESPACE_API_URL, 
        )
        return self.create_from_flow(project_name=project_name, variables=variables, flow=flow)

    def create_from_flow(self, project_name: str=None, variables: dict=None, flow: Flow=None) -> 'Project':
      
        if not flow:
            raise ValueError("Flow must be provided to create a project.")
        
        template_compose = flow.generate_compose(variables=variables, project_name=project_name)
        return self.create_from_compose_yaml(template_compose)
    
    def create_from_compose_yaml(self, compose: yaml):
        """
        Creates a new project.

        Args:
            project_data: The data for creating the project.

        Returns:
            If the request is successful, returns the created project as a JSON object.
            Otherwise, returns the status code and error message.
            https://github.com/diphyx/dxf/blob/main/core/api/bruno/requests/project/create.bru
        """
        url = f'{self.dxflow_url}/api/projects/'
        headers = {"X-SECRET-KEY": self._unit_secrets['RW']}
        compose_string = yaml.dump(compose, default_flow_style=False)
        response = requests.post(url, headers=headers, data=compose_string)
        if response.status_code in [200, 201]:
            project_name = response.json()
            project_detail = self._get_detail(project_name['name'], update=False)
            new_project = self._assign_project(project_detail)
            self.projects[project_detail["name"]] = new_project
            return new_project
        else:
            print(f"Failed to create project: {response.status_code}, {response.text}")
            return None

    def delete(self, project_id):
        """
        Deletes a project.

        Args:
            project_id: The ID of the project to delete.

        Returns:
            If the request is successful, returns a success message.
            Otherwise, returns the status code and error message.
        """
        url = f'{self.dxflow_url}/api/projects/{project_id}/'
        headers = {"X-SECRET-KEY": self._unit_secrets['RW']}
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            return "Project deleted successfully"
        else:
            return response.status_code, response.text
    def _assign_project(self, project_info):    
        return Project(
            name=project_info["name"],
            date=project_info["date"],
            services=project_info.get("services"),
            containers=project_info.get("containers"),
            edges=project_info.get("edges"),
            compose=project_info.get("compose"),
            template=project_info.get("template"),
            unit_secrets=self._unit_secrets,
            dxflow_url=self.dxflow_url
        )
       

class Project:
    """
    A class that represents a project in the DXFlow SDK.
    """

    def __init__(self, name=None, date=None, services=None, containers=None, edges=None, compose=None, template=None,
                 dxflow_url=None, unit_secrets=None):
        """
        Initializes a new instance of the Project class.

        Args:
            project_id: The ID of the project.
            unit_secret (Optional): The unit secret for authentication.
            dxflow_url (Optional): The DXFlow URL.
            project_info (Optional): The project information as a JSON object. ['name', 'date', 'services', 'containers', 'edges', 'compose', 'template']
        """
        self.name = name
        self.date = datetime.datetime.fromtimestamp(int(date) / 1000).strftime('%m-%d-%Y') if date else None
        self._unit_secrets = unit_secrets
        self.dxflow_url = dxflow_url
        self.containers = containers or []
        self.services = services or []
        self.edges = edges or []
        if template:
            if isinstance(template, str):
                try:
                    self.templates = yaml.safe_load(template)
                except yaml.YAMLError as e:
                    print(f"Error parsing template as YAML: {e}")
                    self.templates = {}
            else:
                self.templates = template
        else:
            self.templates = {}
        self.containers = [self._assign_container(container_info) for container_info in self.containers]
        self.compose = yaml.safe_load(compose) if isinstance(compose, str) else compose

    def __str__(self):
        return json.dumps({
            'name': self.name,
            "date": self.date,
            'containers': [str(container) for container in self.containers],
            'services': self.services,
            'templates': self.templates,
            'edges': self.edges,
            "dxflow_url": self.dxflow_url,
        }, indent=4)
    
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
                        unit_secret=self._unit_secrets['RO'], 
                        dxflow_url=self.dxflow_url)
    
    def detail(self, update_data=True, print_info=False):
        """
        Retrieves the details of the project.

        Returns:
            If the request is successful, returns the project details as a JSON object.
            Otherwise, returns the status code and error message.
        """
        url = f'{self.dxflow_url}/api/projects/{self.name}/'
        headers = {"X-SECRET-KEY": self._unit_secrets['RO']}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            project_info = response.json()
            if print_info:
                print("Project details:")
                print(json.dumps(project_info, indent=4))
            if update_data:
                self.name = project_info["name"]
                self.date = datetime.datetime.fromtimestamp(int(project_info["date"]) / 1000).strftime('%m-%d-%Y')
                self.services = project_info.get("services")
                self.containers = [self._assign_container(container_info) for container_info in project_info.get("containers", [])]
                self.edges = project_info.get("edges")
                self.compose = project_info.get("compose")
                self.templates = project_info.get("template")

            return response.json()
        else:
            return response.status_code, response.text

    def status(self):
        status = None
        for container in self.containers:
            c_status = container.get_status()
            if status is None:
                status = c_status 
            else: 
                if c_status == Status.RUNNING:
                    return Status.RUNNING
                if c_status == status:
                    continue

        return status
    
    def status_watcher(self, status=Status.COMPLETED, timeout=600, poll_interval=10):
        for container in self.containers:
            container.status_watcher(status=status, timeout=timeout, poll_interval=poll_interval)
        return status

    def list_containers(self, print_info=True, return_info=False):
        if print_info:
            table_headers = ["Name", "ID", "Status"]
            table_data = []
            for container in self.containers:
                table_data.append({"Name": str(container.name), "ID": str(container.container_id), "Status": str(container.status)})
            print_table(table_data, table_headers)

        if return_info:
            return self.containers
        
    def logs(self, container_id=None, print_info=True, real_time=False, return_info=False):
        if container_id is None:
            contanerlist = self.containers
        else:
            contanerlist = [container for container in self.containers if container.container_id == container_id]
        self._logs = []
        for container in contanerlist:
            log = container.logs(print_info=False)
            log = log["list"]
            self._logs.extend(log)
        if print_info:
            log_viewer(self._logs, real_time=real_time)
        if return_info:
            return self._logs
        else: 
            pass 

    def realtime_logs(self, container_id=None, time_interval=1):
        contanerlist = self.containers
        running_container = next((ctr for ctr in self.containers if ctr.get_status() == Status.RUNNING), None)

        first_time = True
        log_history = False
        while running_container and running_container.get_status() == Status.RUNNING:
            logs_output = running_container.logs(print_info=False)
            if first_time:
                log_viewer(logs_output["list"], new_lines=False)
                log_history = logs_output["list"]
                first_time = False
            else:
                new_logs = logs_output["list"]
                new_logs_lines = [
                    entry for entry in new_logs
                    if entry["date"] not in {old["date"] for old in log_history}
                ]
                log_viewer(new_logs_lines, new_lines=True)
                log_history = new_logs
            time.sleep(time_interval)
        print(f"Project {self.name} is no longer RUNNING.")
    
    def change_status(self, status: CommandStatus):
        # status = CommandStatus.from_string(status)
        
        if status == CommandStatus.UNKNOWN or status not in [CommandStatus.START, CommandStatus.STOP, CommandStatus.PAUSE, CommandStatus.UNPAUSE, CommandStatus.TERMINATE]:
            print(f"Unknown or unsupported command: {status}")
            return None
        
        current_status = self.status()
        if  (current_status == Status.TERMINATED) or \
            (current_status == Status.DESTROYED) or \
            (current_status == Status.PAUSED and status == CommandStatus.PAUSE) or \
            (current_status == Status.RUNNING and status == CommandStatus.START) or \
            (current_status == Status.STOPPED and status == CommandStatus.STOP):            
            print(f"Project is already {current_status.name}, command to {status.name} is omitted")
            return None

        if current_status == Status.PAUSED and status == CommandStatus.START:
            print(f"ERROR: Cannot Start the paused {self.name} project, you an uunpause it: by project.unpause()")
            return None
        
        # Change the status of the project using an HTTP PUT request
        url = f'{self.dxflow_url}/api/projects/{self.name}/{status.value.lower()}/'
        headers = {"X-SECRET-KEY": self._unit_secrets['RW']}
        response = requests.put(url, headers=headers)
        if response.status_code in [202, 204]:
            print(f"Project is signaled to {status.name} successfully")
            return "successfull"
        else:
            raise Exception(f"Failed to {status.name} projrect '{self.name}' with the current status of {current_status}: {response.status_code}, {response.text}")
        
    def start(self):
        """
        Starts the project.
        """
        return self.change_status(CommandStatus.START)

    def stop(self):
        """
        Stops the project.
        """
        return self.change_status(CommandStatus.STOP)
        
    def pause(self):
        """
        Pauses the project.
        """
        return self.change_status(CommandStatus.PAUSE)
    
    def unpause(self):
        """
        Unpauses the project.
        """
        return self.change_status(CommandStatus.UNPAUSE)
    
    def terminate(self):
        """
        Terminates the project.
        """
        return self.change_status(CommandStatus.TERMINATE)
    
    def status(self):
        status_all = [container.get_status() for container in self.containers]
        if not status_all:
            return Status.UNKNOWN
        
        status_all = [s for s in status_all if s != Status.DESTROYED]
        if not status_all:
            return Status.DESTROYED
        
        # If all containers have the same status, return that status.
        if all(s == status_all[0] for s in status_all):
            return status_all[0]

        count_running = status_all.count(Status.RUNNING)
        count_stopped = status_all.count(Status.STOPPED)
        count_paused = status_all.count(Status.PAUSED)

        # If exactly one container is running, return RUNNING.
        if count_running == 1:
            return Status.RUNNING
        # If none are running and exactly one is stopped, return STOPPED.
        elif count_running == 0 and count_stopped == 1:
            return Status.STOPPED
        # If none are running or stopped and exactly one is paused, return PAUSED.
        elif count_running == 0 and count_stopped == 0 and count_paused == 1:
            return Status.PAUSED

        return Status.UNKNOWN
    
    def update(self, command):
        """
        Updates the project.
        """
        # {commands: {instance: []}, environments: {}}
        url = f'{self.dxflow_url}/api/projects/{self.name}/'
        headers = {"X-SECRET-KEY": self._unit_secrets['RW']}
        body = {
            "commands": command,
            "environments": {
                "instance": {
                    "UPDATED": "true"
                }
            }
        }
        response = requests.patch(url, headers=headers, json=body)
        if response.status_code in [202, 204]:
            print("Project updated successfully")
            return "successful"
        else:
            return response.status_code, response.text