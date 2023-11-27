import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Proxy import Proxy

try:
    proxy = Proxy("server")
    proxy.__run()
    print("press ctrl+c to stop")
    while True:
        pass
except KeyboardInterrupt:
    proxy.stop()
