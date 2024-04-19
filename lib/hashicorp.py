import requests
import os


APIVERSION = "2023-06-13"

def getOAuthToken():
    hcpTokenURL = "https://auth.hashicorp.com/oauth/token"

    # Payload with grant type, client credentials, and audience
    payload = {
        'grant_type': 'client_credentials',
        'client_id': os.environ.get("clientID"),
        'client_secret': os.environ.get("clientSecret"),
        'audience': "https://api.hashicorp.cloud",
    }

    # Headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    response = requests.post(hcpTokenURL, data=payload, headers=headers)
    

    if response.status_code == 200:
        # Parse the token from the response
        token = response.json().get('access_token')
        return token
    else:
        print("Failed to retrieve token. Status code:", response.status_code)
        print("Response:", response.text)


def getAppSecret(appName, secretName):   
    # format the API endpoint
    apiendpoint = "https://api.cloud.hashicorp.com/secrets/{}/organizations/{}/projects/{}/apps/{}/open/{}".format(APIVERSION ,os.environ.get("organizationID"), os.environ.get("projectID"), appName, secretName)
    

    # set the headers for the request using the accessToken provided by getOAuthToken()
    headers = {
        'Authorization': 'Bearer {}'.format(getOAuthToken())
    }

    response = requests.get(apiendpoint, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to get secret. Hitting the url\napi endpoint: {}\nreturned status code: ".format(apiendpoint), response.status_code)
        print("Response:", response.text)