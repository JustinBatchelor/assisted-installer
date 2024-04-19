# assisted-installer
Python repository to install a bare metal openshift cluster to a proxmox virtual environment using the Red Hat Assisted Installer API 


## Requirements

### Hashicorp Cloud Platform (HCP)

**HCP Topology**

- Organization -> Project(s) -> Service(s) [e.g Vault Secrets] -> Application -> Key/Value (secret)

This code is opinionated, and assumes that you are using the Hashicorp Cloud Platform (HCP) | Vault Secrets service to store sensitive information/credentials that you do not want exposed within the repo itself. An example would be the `pull_secret` and `token` that are used for authenticating against the Red Hat Assisted Installer. This service as of 4/19/24 is free, and allows us to store up to 25 secrets. We can also utilize the [HCP API](https://developer.hashicorp.com/hcp/api-docs/vault-secrets) to retrieve secrets as necessary.

In order for the code to function properly, we will need to set a few environment variables to provide authentication to the HCP API such that we can retrieve the secret values for other sensitive information.

**Environment Variables** 

- `clientID`: This is the clientID that is associated with the service principal in HashiCorp Cloud Platform.

- `clientSecret`: This is the clientSecret that is associated with the service principal in HashiCorp Cloud Platform.

- `organizationID`: The HashiCorp Cloud Platform organization ID that owns the Vault Secrets application

- `projectID`: The HashiCorp Cloud Platform project ID where the Vault Secrets application is located

You can find the `organizationID` and `projectID` in the resective settings tab in HCP. However, in order to get the clientID and clientSecret, you will need to navigate to the `Projects` -> `<Project Name>` -> `Access Control (IAM)` -> `Service Principals` tab within your organization. Create a service principal with the `Contributer Role` and generate keys. This will populate a `clientID` and `clientSecret` that the code will use to authenticate to the HCP API
