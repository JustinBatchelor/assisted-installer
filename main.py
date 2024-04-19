from lib import hashicorp

print(hashicorp.getAppSecret("assisted-installer", "pull_secret")['secret']['version']['value'])