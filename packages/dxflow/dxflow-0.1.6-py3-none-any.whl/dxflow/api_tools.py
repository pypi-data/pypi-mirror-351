import requests

def make_api_request(method, url, headers=None, data=None, params=None):
    """
    Centralized API request function.

    :param method: HTTP method (e.g., 'get', 'post').
    :param url: URL for the API endpoint.
    :param headers: Optional headers to send with the request.
    :param data: Optional body to send with the request, for POST, PUT, etc.
    :param params: Optional URL parameters to send with the request.
    :return: JSON response data on success, or tuple of status code and error text on failure.
    """
    try:
        response = requests.request(method, url, headers=headers, params=params, data=data)
        
        # Check if the response was successful
        response.raise_for_status()
        return response.json()  # Return JSON data on success
    except requests.HTTPError as http_err:
        # Handle HTTP errors
        return response.status_code, str(http_err)
    except Exception as err:
        # Handle other potential errors (e.g., network issues)
        return None, str(err)