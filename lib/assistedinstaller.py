import requests, json, jmespath
from urllib.parse import urlencode
from lib import logging


class assistedinstaller:
    def __init__(self, offline_token, pull_secret):
        self.offlineToken = offline_token
        self.pullSecret = pull_secret
        self.apiBase = "https://api.openshift.com/"


    def getAccessToken(self):
        # URL for the token request
        url = "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"

        # Headers to be sent with the request
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Data to be sent in the request, explicitly encoding each variable
        data = urlencode({
            "grant_type": "refresh_token",
            "client_id": "cloud-services",
            "refresh_token": self.offlineToken
        })


        # Make the POST request
        response = requests.post(url, headers=headers, data=data)

        # Handle response
        if response.status_code == 200:
            # Extract access token from the response JSON
            access_token = response.json().get("access_token")
            return access_token
        else:
            # Print error message if something went wrong
            logging.quitMessage("Failed to retrieve access token. Messsage from API: {}".format(response.text))


    def getCluster(self, name):
        url = self.apiBase + "api/assisted-install/v2/clusters"
        headers = {
            "Authorization": "Bearer {}".format(self.getAccessToken()),
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        # JMESPath query
        query = f"[?name == '{name}']"

        # Execute and return the query
        return jmespath.search(query, json.loads(response.text))


    def deleteCluster(self, name):
        cluster = self.getCluster(name)
        if cluster:
            # print(cluster)
            url = self.apiBase + "api/assisted-install/v2/clusters/{}".format(cluster[0]['id'])
            headers = {
                "Authorization": "Bearer {}".format(self.getAccessToken()),
                "Content-Type": "application/json"
            }
            response = requests.delete(url, headers=headers)
            print(response.text)
            if response.status_code != 204:
                logging.quitMessage("Recieved an error from API when trying to delete the cluster: {}".format(response.text))
            return True
        else:
            logging.errorMessage("Assisted Installer API did not return a match for the cluster name: {}".format(name))
            return False