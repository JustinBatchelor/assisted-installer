## Code to disable creating pycache dir after running
import sys
sys.dont_write_bytecode = True
###################################################


from lib import hashicorp, tools, logging

import typer


hcp = hashicorp.hashicorp()

app = typer.Typer()


@app.command()
def deploycluster(name: str = "", basedomain: str = "", version: str = tools.fetchOpenshiftVersion()):
    if not tools.validateName(name):
        logging.quitMessage("name: {} - is not a valid name that can be used with the assisted-installer. Please ensure the name conforms to the following regular expression: {}".format(name, "^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"))
    
    if not tools.validateDomain(basedomain):
        logging.quitMessage("basedomain: {} - is not a valid domain. Please double check your imput and try again".format(basedomain))
    
    if not tools.validateVersion(version):
        logging.quitMessage("version - {} - is not a valid version. The code will default to the lastest supported version of openshift. Please double check the version you passed and ensure it conforms to the following regualar expression (only x.xx versions supported right now): {}".format(version, "^[0-9]+\.[0-9]+$"))
    
    # If we made it here then we should 
    
    print("Command to deploy cluster")



@app.command()
def removecluster(name: str):
    print("Command to remove fully delete openshift cluster")


if __name__ == '__main__':
    app()