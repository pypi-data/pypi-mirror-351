import json
import yaml

from .api_tools import make_api_request
from .config import NAMESPACE_API_URL
from .utils import print_table, FLowRegisteryStatus

class FlowRegisteryManager:
    """
    A class that manages flow packages in a namespace.

    Args:
        namespace_pointer (str): The pointer to the namespace.
        namespace_secret (str): The secret key for the namespace.
        api_url (str, optional): The URL of the API. Defaults to NAMESPACE_API_URL.

    Attributes:
        api_url (str): The URL of the API.
        namespace_pointer (str): The pointer to the namespace.
        headers (dict): The headers for API requests.
        flow_packages (list): The list of flow packages.
        _table_headers (list): The headers for the table display.

    Methods:
        publish: Publishes a new flow package.
        update_flow_package: Updates an existing flow package.
        update_template: Updates the template of a flow package.
        get: Retrieves a flow package.
        get_list: Retrieves a list of flow packages.
        list: Lists flow packages.
        activate: Activates a flow package.
        deactivate: Deactivates a flow package.
        get_flow_pointer: Retrieves the ID of a flow package.

    """

    def __init__(self, namespace_pointer, namespace_secret, api_url=NAMESPACE_API_URL):
        """
        Initializes a new instance of the FlowRegisteryManager class.

        Args:
            namespace_pointer (str): The pointer to the namespace.
            namespace_secret (str): The secret key for the namespace.
            api_url (str, optional): The URL of the API. Defaults to NAMESPACE_API_URL.

        """
        self.api_url = api_url
        self.namespace_pointer = namespace_pointer
        self.headers = {"X-SECRET-KEY": namespace_secret}
        self.flow_list = self.get_list()

        
        

    def publish(self, name, description=None, properties=None, tags=None, arch="AMD64", color=None, 
                icon=None, logo=None, image=None, logo_url=None, image_url=None):
        """
        Publishes a new flow package.

        Args:
            name (str): The name of the flow package.
            description (str, optional): The description of the flow package.
            properties (dict, optional): The properties of the flow package.
            tags (list, optional): The tags of the flow package.
            arch (str, optional): The architecture of the flow package. Defaults to "AMD64".
            color (str, optional): The color of the flow package.
            icon (str, optional): The icon of the flow package.
            logo (str, optional): The logo of the flow package.
            image (str, optional): The image of the flow package.
            logo_url (str, optional): The URL of the logo of the flow package.
            image_url (str, optional): The URL of the image of the flow package.

        Returns:
            dict: The response from the API.

        """
        url = f"{self.api_url}/namespaces/{self.namespace_pointer}/flows/"
        body = {
            "name": name,
            "description": description,
            "properties": properties,
            "tags": tags
        }
        response = make_api_request('post', url, headers=self.headers, data=body)
        return self._handle_response(response)

    
    def update_flow_package(self, flow_pointer, update_data):
        """
        Updates an existing flow package.

        Args:
            flow_pointer (str): The pointer to the flow package.
            update_data (dict): The data to update the flow package.

        Returns:
            dict: The response from the API.

        """
        url = f"{self.api_url}/namespaces/{self.namespace_pointer}/flows/{flow_pointer}/"
        response = make_api_request('patch', url, headers=self.headers, data=update_data)
        return self._handle_response(response)

    def update_template(self, flow_pointer, template_data):
        """
        Updates the template of a flow package.

        Args:
            flow_pointer (str): The pointer to the flow package.
            template_data (dict): The template data to update the flow package.

        Returns:
            dict: The response from the API.

        """
        url = f"{self.api_url}/namespaces/{self.namespace_pointer}/flows/{flow_pointer}/template/"
        headers = {"X-SECRET-KEY": self.headers["X-SECRET-KEY"]}
        body = template_data
        response = make_api_request('patch', url, headers=headers, data=body)
        return self._handle_response(response)

    def get(self, flow_pointer):
        
        url = f"{self.api_url}/namespaces/{self.namespace_pointer}/flows/{flow_pointer}/"
        flow = make_api_request('get', url, headers=self.headers)
        return Flow(
                    name=flow["name"],
                    template=flow["template"],
                    pointer=flow["pointer"],
                    user=flow["user"],
                    description=flow.get("description"),
                    properties=flow.get("properties", {}),
                    tags=flow.get("tags", []),
                    environments=flow.get("environments", []),
                    visibility=flow.get("visibility", "PRIVATE"),
                    status=flow.get("status"),
                    created_at=flow.get("created_at"),
                    updated_at=flow.get("updated_at"),
                    state=flow.get("state"),
                    verified=flow.get("verified"),
                )
    @classmethod
    def get_by_flow_name(cls, name, namespace_pointer, namespace_secret, api_url=NAMESPACE_API_URL):
        """
        Retrieve a flow package by name without needing to manually instantiate FlowRegisteryManager.

        Args:
            name (str): The name of the flow package.
            namespace_pointer (str): The pointer to the namespace.
            namespace_secret (str): The secret key for the namespace.
            api_url (str, optional): The URL of the API. Defaults to NAMESPACE_API_URL.
            update_list (bool, optional): Whether to update the flow list prior to search. Defaults to True.

        Returns:
            Flow: The retrieved Flow instance.
        """
        instance = cls(namespace_pointer, namespace_secret, api_url=api_url)
        return instance.get_by_name(name, update_list=True)
    
    def get_by_name(self, name, update_list=True):
        if update_list:
            self.flow_list = self.get_list()
        pointer = self.get_flow_pointer(name=name, update_list=False)
        return self.get(flow_pointer=pointer)
       


    def get_list(self, filters=None):
        """
        Retrieves a list of flow packages.

        Args:
            filters (str, optional): The filters to apply to the list. Defaults to "tags=AMD64&verified=true".

        Returns:
            dict: The response from the API.

        """
        
        url = f"{self.api_url}/namespaces/{self.namespace_pointer}/flows/"
        if filters:
            filter_query = "&".join([f"{key}={value}" for key, value in filters.items()])
            url += f"?{filter_query}"
  
        response = make_api_request('get', url, headers=self.headers)
        self._handle_response(response)["list"]
        return self._handle_response(response)["list"]


    def list(self, filters={"tags": "AMD64", "verified": True}, table=True):
        """
        Lists flow packages.

        Args:
            filters (str, optional): The filters to apply to the list. Defaults to {"tags": "AMD64", "verified": True}
            table (bool, optional): Whether to display the list as a table. Defaults to True.

        Returns:
            dict: The response from the API.

        """
        flow_list = self.get_list(filters)
        # self.flow_list = response["list"]
        self._table_headers = ["Name", "Pointer", "Tags", "Status", "Verified"]
        if table:
            table_data = []
            # keys: ['pointer', 'user', 'name', 'description', 'template', 'properties', 'tags', 'environments', 'visibility', 'status', 'created_at', 'updated_at', 'state', 'verified']
            for sw in flow_list:
                table_data.append({
                    "Name": sw['name'],
                    "Pointer": sw['pointer'],
                    "Tags": sw['tags'][:3],
                    "Status": sw['status'],
                    "Verified": sw['verified'],
                })         
            print_table(table_data, self._table_headers)
        else:
            print(self.flow_list)
        return self.flow_list
    
    @classmethod
    def available_flows(cls, name, namespace_pointer, namespace_secret, api_url=NAMESPACE_API_URL):
        instance = cls(namespace_pointer, namespace_secret, api_url=api_url)
        return instance.list()
       

    def activate(self, flow_pointer):
        """
        Activates a flow package.

        Args:
            flow_pointer (str): The pointer to the flow package.

        Returns:
            dict: The response from the API.

        """
        url = f"{self.api_url}/namespaces/{self.namespace_pointer}/flows/{flow_pointer}/active/"
        response = make_api_request('put', url, headers=self.headers)
        return self._handle_response(response, success_message="flow package activated successfully")

    def deactivate(self, flow_pointer):
        """
        Deactivates a flow package.

        Args:
            flow_pointer (str): The pointer to the flow package.

        Returns:
            dict: The response from the API.

        """
        url = f"{self.api_url}/namespaces/{self.namespace_pointer}/flows/{flow_pointer}/inactive/"
        response = make_api_request('put', url, headers=self.headers)
        return self._handle_response(response, success_message="flow package deactivated successfully")

    def get_flow_pointer(self, name=None, update_list=True):
        
        if update_list:
            self.flow_list = self.get_list()
        for flow in self.flow_list:
            if flow.get("name") == name:
                return flow.get("pointer")


    def _handle_response(self, response, table=False, success_message=None):
        """
        Handles the API response.

        Args:
            response (dict or tuple): The response from the API.
            table (bool, optional): Whether to display the response as a table. Defaults to False.
            success_message (str, optional): The success message. Defaults to None.

        Returns:
            str or dict: The formatted response.

        """
        if isinstance(response, tuple):
            status_code, error_message = response
            return f"Error {status_code}: {error_message}"
        else:
            if success_message:
                return success_message
            if table:
                table_data = self._prepare_for_print(response)
                print_table(table_data, self._table_headers)
            return response

class Flow:
    def __init__(self, name, template, pointer=None, user={}, description=None, properties={}, tags=[], environments=[], visibility="PRIVATE", status=None, created_at=None, updated_at=None, state=None, verified=None):
        if name is None or template is None:
            raise ValueError("Both 'name' and 'template' are required fields.")

        if visibility not in ["PRIVATE", "PUBLIC"]:
            raise ValueError("The 'visibility' field must be either 'PRIVATE' or 'PUBLIC'.")

        self.pointer = pointer
        self.user = user
        self.name = name
        self.description = description
        self.template = template # self.load_template(template)
        self.properties = properties or {}
        self.tags = tags or []
        self.environments = environments or []
        self.visibility = visibility
        self.status = FLowRegisteryStatus.from_string(status)
        if self.status == FLowRegisteryStatus.UNKNOWN:
            raise ValueError(f"Invalid status: {status}. Valid statuses are: {', '.join([status.value for status in FLowRegisteryStatus])}")

        self.created_at = created_at
        self.updated_at = updated_at
        
        self.state = state
        
        self.verified = verified

    def generate_compose(self, variables: dict=None, project_name: str= None) -> yaml:
        
        template = load_template(self.template)
        profile_name = choose_profile(template["variables"].get("profiles", {}), variables)
        # Validate variables
        if variables is None:
            variables = {}
        for key, value in variables.items():
            if key not in template["variables"]:
                raise ValueError(f"Variable '{key}' is not defined in the template.")

            template["compose"] = template["compose"].replace(f"{{{{ {key} }}}}", str(value))
           
        
        for var in template["variables"]:
            values = template["variables"][var]
            if var not in variables:
                default = values.get("default", "")
                if values.get("required", False):
                    print(f"Variable '{var}' is required but not provided, its default value will be used: {default}")
                template["compose"] = template["compose"].replace(f"{{{{ {var} }}}}", default)

        if (project_name is not None) and (len(project_name) > 0):
            # Replace the first occurrence of "name:" followed by a newline with "name: project_name\n"
            template["compose"] = template["compose"].replace(
            "name:", f"name: {project_name}\n", 1
            )

        compose_yaml =yaml.safe_load(template["compose"])
        # Filter the services to keep only those that match the selected profile
        services = compose_yaml.get("services", {})
        filtered_services = {}
        for svc_name, svc_details in services.items():
            profiles = svc_details.get("profiles", [])
            if profile_name in profiles:
                filtered_services[svc_name] = svc_details
        compose_yaml["services"] = filtered_services

        # bg: fix this, we should be able to use multi-line commands in compose files
        for svc in compose_yaml.get("services", {}).values():
            svc["command"] = svc["command"].replace(" \ ","  ").replace("\n", " ")
            svc["command"] = svc["command"].strip()
        return compose_yaml
    
    def create_project(self, project_name=None, variables = {}, compute_unit=None, **kwargs):
        
        if not self.template:
            raise ValueError("No template available for this flow.")

        template_compose = self.generate_compose(variables=variables, project_name=project_name)
        
        # Create a project using the compute unit and the updated template
        if compute_unit.projects is None:
            compute_unit.get_projects()
            
        project = compute_unit.projects.create_from_compose_yaml(compose=template_compose)
        
        return project
       
    def _extract_enviroment_variables(self, env_info):
        env_variables = {}
        for key, value in env_info.items():
            if isinstance(value, str) and "{{" in value and "}}" in value:
                env_variables[key] = value.split("{{")[1].split("}}")[0].strip()
            else:
                env_variables[key] = value
        return env_variables
    
    def get_variables(self):
        variables = load_template(self.template).get("variables", {})
        return variables
        
    def display_variables(self, table=True):
        """
        Displays the variables in the template along with their descriptions, hints, and default values or options.

        Args:
            table (bool, optional): Whether to display the variables as a table. Defaults to True.

        Returns:
            None
        """
        variables = self.get_variables()
        if not variables:
            print("No variables found in the template.")
            return

        if table:
            table_data = []
            self._table_headers = ["Variable Name", "Description", "Hint", "Default Value", "Options"]
            for var_name, var_details in variables.items():
                if var_name == "profiles":
                    continue
                options = []
                if "options" in var_details:
                    for option in var_details["options"]:
                        if isinstance(option, dict):
                            options.append(option.get('label', option.get('value', 'Unknown')))
                        else:
                            options.append(option)
                table_data.append({
                    "Variable Name": var_name,
                    "Description": var_details.get('label', 'No description provided'),
                    "Hint": var_details.get('hint', 'No hint provided'),
                    "Default Value": var_details.get('default', 'None'),
                    "Options": ", ".join(options) if options else "None"
                })
            print_table(table_data, self._table_headers)
        else:
            print(json.dumps(variables, indent=4))
        
    def __str__(self) -> str:
        return json.dumps({
            "pointer": self.pointer,
            "user": self.user,
            "name": self.name,
            "description": self.description,
            "template": self.template,
            "properties": self.properties,
            "tags": self.tags,
            "environments": self.environments,
            "visibility": self.visibility,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "state": self.state,
            "verified": self.verified
        }, indent=4)

def choose_profile(template_profiles, variables=None):
   
    extracted_profiles = []
    if variables is None:
        variables = {}
    # Sorting keys so profiles are processed in alphabetical order
    for profile_name in sorted(template_profiles.keys()):
        profile_data = template_profiles[profile_name]
        # Gather allowed option values
        allowed_values = [option.get("value") for option in profile_data.get("options", [])]
        
        if profile_name in variables:
            selected_value = variables[profile_name]
            if selected_value in allowed_values:
                extracted_profiles.append(selected_value)
            else:
                # Variable provided but its value is not valid, fallback to default
                extracted_profiles.append(profile_data.get("default"))
        else:
            # No variable provided, use the default value from the profile
            extracted_profiles.append(profile_data.get("default"))
    profile_name = ""
    for profile in extracted_profiles:
        if profile_name == "default" and profile == "default":
            continue
        if profile_name == "":
            profile_name = profile
        else:
            profile_name = profile_name+ "_"+ profile

        
    return profile_name

def load_template(template):
    """
    Retrieves the template of the flow and optionally saves it to a YAML file.

    Args:
        save_file (str, optional): The file path to save the template. Defaults to None.

    Returns:
        dict: The parsed template data.
    """
    if not template:
        raise ValueError("No template available for this flow.")

    try:
        # Split the template into variables and compose sections
        sections = template.split('---\n', 1)
        if len(sections) != 2:
            raise ValueError("Template must contain two sections separated by '---'.")

        # Parse the variables and compose sections
        variables_section = yaml.safe_load(sections[0])
        profiles_section = {}
        if isinstance(variables_section, dict):
            profiles_found = {}
            for key in list(variables_section.keys()):
                if "DOCKER_COMPOSE_PROFILE" in key:
                    profiles_found[key] = variables_section.pop(key)
                if profiles_found:
                    variables_section["profiles"] = profiles_found
        

        placeholder_safe_section = sections[1].replace("{{", "__JINJA_START__").replace("}}", "__JINJA_END__")
        compose_section = yaml.safe_load(placeholder_safe_section)


        template_data = {
            "variables": variables_section,
            "compose": sections[1],
            "compose_yaml": compose_section  
        }
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing template: {e}")

    return template_data