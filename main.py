## Code to disable creating pycache dir after running
import sys, typer, requests, datetime, time
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

    # If we made it here then we should be in the clear for begining the process of installing a cluster.
    # currently we only support two sizes
    if size == "sno":
        # clusterInfraBundle - a dict containing the cluster object and infrastructure environment needed 
        #                      created after registering a new cluster with the assisted installer api
        #  return dict{
        #       'cluster': <cluster>,
        #       'infra': <infraenv>,
        #   }
        clusterInfraBundle = installer.registerSNOCluster(name, version, basedomain)

        # upload the iso file by url
        pve.uploadISO(clusterInfraBundle['infra']['download_url'], name)

        # define vm in proxmox
        vmID = pve.defineVM(name)

        # start the vm we recently created
        pve.startVM(vmID)

        """
        At this point, we have:
        
        1.) registered a cluster with assisted installer
        2.) registered an infra env with the assisted installer
        3.) created a vm in proxmox and started the vm

        Now we just need to query the assisted installer api and wait for it to pass all preflight validation checks...
        
        This should be entirely automated, however it is possible that definitions may change in the furture
        so we should only wait around 5 minutes before we quit checking the cluster to see if it passed the preflight
        validations and error out.

        In other words, if it takes longer than 5 minutes to pass preflight validation from assisted installer. 
        Then something has probably gone wrong, and will require manual intervention
        """
        endtime = datetime.datetime.now() + datetime.timedelta(minutes=5)

        while installer.getCluster(name)[0]['status'] != 'ready':
            if datetime.datetime.now() >= endtime:
                logging.quitMessage("Cluster failed to move to ready state within 5 minutes. Please review your dashboard for manual intervention")

            logging.logMessage("Waiting for cluster status to be 'ready'")
            logging.prettyPrint(f"{installer.getCluster(name)}")
            logging.logMessage("Sleeping for 30 seconds before retrying")
            time.sleep(30)
        
        # begin cluster installation via api
        installer.installCluster(clusterInfraBundle['cluster']['id'])

        while installer.getCluster(name)[0]['status'] != 'installed':
            if 'total_percentage' in installer.getCluster(name)[0]['progress']:
                logging.logMessage(f"Installation is {installer.getCluster(name)[0]['progress']['total_percentage']}% complete.")
            else: 
                logging.logMessage(f"Installation is 0% complete.")
            time.sleep(30)  


    elif size == "compact":
        logging.quitMessage("Path to create a compact openshift cluster (3 master nodes)... UNDER CONSTRUCTION")
    else: 
        logging.quitMessage("size: {} - is not supported yet".format(size))


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
    logging.logMessage(f"Found {len(deleteVMs)} VM's to delete from proxmox")
    for vm in deleteVMs:
        # delete vm
        pve.deleteVM(vm)
    # delete the iso file that was created and uploaded to pve
    pve.deleteISO(name)

    # finally, delete the cluster via the API
    installer.deleteCluster(name)


@app.command()
def temp(name: str = ""):
    # create hcp instance
    hcp = hashicorp.hashicorp()
    # get assisted installer token value from hashicorp
    token = hcp.getAppSecret("assisted-installer", "token")['secret']['version']['value']
    # get assisted installer pull_secret value from hashicorp
    pullSecret = hcp.getAppSecret("assisted-installer", "pull_secret")['secret']['version']['value']
    # create assisted installer instance
    installer = assistedinstaller.assistedinstaller(token, pullSecret)
    installer.deleteInfrastructureEnvironments()

if __name__ == '__main__':
    app()