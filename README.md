# assisted-installer
Python repository to install a bare metal openshift cluster to a proxmox virtual environment using the Red Hat Assisted Installer API.

## Description
A cli written in python to configure, deploy, and manage Red Hat OpenShift clusters using the Red Hat Assisted Installer and your Red Hat account. The application will also interface with a local proxmox virutal environment API to manage the virtual machine configurations backing the cluster, Currently, there are two sizes supported

| Size | Control-Nodes | CPU (per-node) | Memory (per-node) | Storage (per-node) |
| ---  | ------------- | --- | ------ | ------- |
| sno (single node openshift) | 1 | 8 vcpu | 32000GiB | 200GiB | 
| compact - (##IN DEVELOPMENT##) | 3 | 4 | 16GiB | 200GiB| 

The application utilizes the Hashicorp Cloud Platform - Vault Secrets API, as a secure way to interface with sensitive information such as admin tokens, passwords, and secrets that will be needed for authentication across the various services this project uses.

## Commands


### deploycluster

    $ python ./main.py deploycluster --name=<cluster-name> --version=<cluster-version> --basedomain=<domain> --size=<size>


**Options**

```
  name: name 
    required: true
    default: ""
    type: str
    description: name of the openshift cluster to create
    example: ocp

  name: version
    required: false
    default: latest stable release
    type: str
    description: openshift version (major.minor), defaults to latest stable release
    example: 4.15, 4.14

  name: basedomain
    required: true
    default: ""
    type: str
    description: base domain to build the openshift routes 
    example: "example.com"

  name: size
    required: false
    default: "sno"
    type: str
    description: the cluster size that you want to deploy
    example: "compact"
    choices: ["sno", "compact"]
```


### removecluster

    $ python ./main.py removecluster --name=<cluster-name>

**Options**

```
  name: name 
    required: true
    default: ""
    type: str
    description: name of the openshift cluster to delete
    example: ocp

```


## Dependancies

**Python Version**

- `python3.12.2+`

**Modules**

- refer to `requirements.txt`


**Environment Variables** 

- `clientID`: This is the clientID that is associated with the service principal in HashiCorp Cloud Platform.

- `clientSecret`: This is the clientSecret that is associated with the service principal in HashiCorp Cloud Platform.

- `organizationID`: The HashiCorp Cloud Platform organization ID that owns the Vault Secrets application

- `projectID`: The HashiCorp Cloud Platform project ID where the Vault Secrets application is located

- `proxmoxServiceIP`: The local IP of your proxmox virtual environment

- `proxmoxServicePort`: The port that your proxmox virtual environment is running on

- `proxmoxUser`: The username@pam used for authentication against the pve API

- `proxmoxNode`: The name of the proxmox node to connect to


**Vault Secrets**

| Apps | Key(s) |
| ------- | --- |
| assisted-installer | `[pull_secret, token]` |
| proxmox | `[password]` |

### Hashicorp Cloud Platform (HCP)

**HCP Topology**

- Organization -> Project(s) -> Service(s) [e.g Vault Secrets] -> Application -> Key/Value (secret)

![alt text](./docs/pictures/hcp-topo.png)

This code is opinionated, and assumes that you are using the Hashicorp Cloud Platform (HCP) | Vault Secrets service to store sensitive information/credentials that you do not want exposed within the repo itself. An example would be the `pull_secret` and `token` that are used for authenticating against the Red Hat Assisted Installer. This service as of 4/19/24 is free, and allows us to store up to 25 secrets.

In order for the code to function properly, we will need to set a few environment variables to provide authentication to the HCP API such that we can retrieve the secret values for other sensitive information.

You can find the `organizationID` and `projectID` in their respective settings tab in HCP. However, in order to get the clientID and clientSecret, you will need to navigate to the `Projects` -> `<Project Name>` -> `Access Control (IAM)` -> `Service Principals` tab within your organization. Create a service principal with the `Contributer Role` and generate keys. This will populate a `clientID` and `clientSecret` that the code will use to authenticate to the HCP API



### RedHat Assisted Installer API

The RedHat Assisted Installer API requires that you have a RedHat Hybrid Cloud Account giving you access to a pull secret and token. These two credentials are assumed to be stored in a HCP Vault Secrets application named `assisted-installer`. 

At a high level, this code uses the Assisted Installer API to first, register a `cluster` object, and an `infrastruture environment` object. An `infrastructure-environment` has a one-to-many relationship with `cluster` objects and tell the assisted installer what 'kind' of cluster we are trying to install. This defines the requirements the Assisted Installer will look for before attempting to install a cluster. An `infrastructure-environment` also provides a preloaded ISO file we can use to boot our OpenShift nodes. Once we have this ISO file, we can utilize the `proxmoxcluster` class to upload the ISO file via URL 

Once the VM is configured and started, our Node will then begin to communicate with the assisted installer and automagically configure itself ready for installation. Once a cluster has passed it's preflight checks it's time to begin the installation process.


### Proxmox Virtual Environment 8.0.3

Proxmox Virtual Environment is a complete open-source platform for enterprise virtualization. With the built-in web interface you can easily manage VMs and containers, software-defined storage and networking, high-availability clustering, and multiple out-of-the-box tools using a single solution.

At a high level, this code uses the Proxmox REST API to create a virutal machine with the appropriate networking, and hardware configurations (e.g: cpu, memory, and storage), that boots from the ISO file generated by the `infrastructure-environment` from the Assisted Installer.


## References

- [Hashicorp Cloud Platform | Vault Secrets](https://developer.hashicorp.com/hcp/docs/vault-secrets)

- [RedHat Assisted Installer API | Docs](https://developers.redhat.com/api-catalog/api/assisted-install-service#content-operations) 

- [Proxmox Virtual Environment](https://www.proxmox.com/en/proxmox-virtual-environment/overview)

- [Proxmox Virtual Environment | API](https://pve.proxmox.com/pve-docs/api-viewer/)
