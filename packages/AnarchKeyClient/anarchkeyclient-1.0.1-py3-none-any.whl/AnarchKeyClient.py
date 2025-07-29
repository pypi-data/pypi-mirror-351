import requests as rq
import json
BASE_URL = "https://anarchkey.pythonanywhere.com/"

class AnarchKeyClient:
    """
    Client for interacting with the AnarchKey API to retrieve stored API keys.

    This client provides methods to securely retrieve API keys from the AnarchKey
    vault service without hardcoding sensitive information in your codebase.
    """
    def __init__(self, api_key, username):
        """
        Initialize the AnarchKey client.

        Args:
            api_key (str): Your AnarchKey API key for authentication
            username (str): Your AnarchKey username for authentication
        """
        self.api_key = api_key
        self.base_url = BASE_URL
        self.username = username

    def get_api_key(self, project_name):
        """
        Retrieve an API key for a specific project from the AnarchKey vault.

        Args:
            project_name (str): The name of the project whose API key you want to retrieve

        Returns:
            dict: Response containing success status, API key (if successful),
                 and message (if unsuccessful)
                 Format: {"success": bool, "key": str, "message": str}
        """
        payload = json.dumps({
            "project_name": project_name,
            "username": self.username,
            "api_key": self.api_key
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = rq.request("POST", self.base_url + "get_api_key", headers=headers, data=payload)
        response = response.json()
        if response["api_key"]["success"]:
            return response["api_key"]
        return response["api_key"]