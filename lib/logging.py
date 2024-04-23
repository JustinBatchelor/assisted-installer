import pprint


def prettyPrint(json):
    logMessage(pprint.pprint(json))


def logMessage(msg):
    print("LOG: {}".format(msg))

def errorMessage(msg):
    print("ERR: {}".format(msg))


def quitMessage(msg):
    print("ERR: {}".format(msg))
    quit()

