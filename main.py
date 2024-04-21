## Code to disable creating pycache dir after running
import sys, typer, requests
sys.dont_write_bytecode = True
###################################################


from lib import hashicorp, tools, logging, assistedinstaller, proxmox
from urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)



app = typer.Typer()


@app.command()
def deploycluster(name: str = "", basedomain: str = "", version: str = tools.fetchOpenshiftVersion(), size: str = "sno"):
    if not tools.validateName(name):
        logging.quitMessage("name: {} - is not a valid name that can be used with the assisted-installer. Please ensure the name conforms to the following regular expression: {}".format(name, "^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"))
    
    if not tools.validateDomain(basedomain):
        logging.quitMessage("basedomain: {} - is not a valid domain. Please double check your imput and try again".format(basedomain))
    
    if not tools.validateVersion(version):
        logging.quitMessage("version: {} - is not a valid version. The code will default to the lastest supported version of openshift. Please double check the version you passed and ensure it conforms to the following regualar expression (only x.xx versions supported right now)".format(version))
    
    if not tools.validateSize(size):
        logging.quitMessage("size: {} - is not a valid size. Please choose from one of the following options [sno, compact]. The code currently defaults to installing a single node openshift cluster".format(size))
    
    # If we made it here then we should be in the clear for begining the process of installing a cluster.
    # currently we only support two sizes
    if size == "sno":
        print("Path to create a single node openshift cluster")
    elif size == "compact":
        print("Path to create a compact openshift cluster (3 master nodes).")
    else: 
        logging.quitMessage("size: {} - is not supported yet".format(size))
    
    print("Command to deploy cluster")


@app.command()
def removecluster(name: str = ""):
    if not tools.validateName(name):
        logging.quitMessage("name: {} - is not a valid name that can be used with the assisted-installer. Please ensure the name conforms to the following regular expression: {}".format(name, "^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"))

    # create hcp instance
    hcp = hashicorp.hashicorp()
    
    # get assisted installer token value from hashicorp
    token = hcp.getAppSecret("assisted-installer", "token")['secret']['version']['value']
    # get assisted installer pull_secret value from hashicorp
    pullSecret = hcp.getAppSecret("assisted-installer", "pull_secret")['secret']['version']['value']
    # get the proxmox password from hashicorp
    password = hcp.getAppSecret("proxmox", "password")['secret']['version']['value']
    # create assisted installer instance
    installer = assistedinstaller.assistedinstaller(token, pullSecret)
    # create proxmox cluster instance
    pve = proxmox.proxmoxcluster(password)
    # find all vms backing the cluster in proxmox
    deleteVMs = pve.getVMsWithTag(name)
    # loop through each vm to delete
    for vm in deleteVMs:
        # delete vm
        pve.deleteVM(vm)

    ## Third we need can delete the cluster via the API
    installer.deleteCluster(name)


@app.command()
def testproxmoxer():
    hcp = hashicorp.hashicorp()
    password = hcp.getAppSecret("proxmox", "password")['secret']['version']['value']
    pve = proxmox.proxmoxcluster(password)
    print(pve.getVMsWithTag("test-ocp"))
    vms = pve.getVMsWithTag("test-ocp")
    for vm in vms:
        print(pve.deleteVM(vm))

if __name__ == '__main__':
    app()