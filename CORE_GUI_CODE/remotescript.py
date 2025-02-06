
from rumrunner import runner
REMOTE_HOST_IPADDR="192.168.4.212"
REMOTE_HOST_USER="pi"
r = runner.Runner(REMOTE_HOST_IPADDR, REMOTE_HOST_USER)
rval, stdout, stderr = r.run('/path/to/local/script.py')
if rval:
    print stderr
else:
    print stdout