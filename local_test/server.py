import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Proxy import Proxy

proxy = Proxy("server")
proxy.run()
