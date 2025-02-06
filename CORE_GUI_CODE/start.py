import os
import time
os.system("lxterminal -e bash -c \"mavproxy.py --out=127.0.0.1:14551 --out=127.0.0.1:14550; exec bash\"&")
time.sleep(10)
os.system("lxterminal -e bash -c \"python connectiontest1.py; exec bash\"&")
