import subprocess
import os
import re
def findProcess( processId ):
    ps= subprocess.Popen("ps aux | grep "+processId, shell=True, stdout=subprocess.PIPE)
    output = ps.stdout.read()
    print output
    ps.stdout.close()
    ps.wait()
    return output
def isProcessRunning( processId):
    output = findProcess( processId )
    if re.search(processId, output) is None:
        return true
    else:
        return False


print isProcessRunning('/usr/bin/mongod')