import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Proxy import Proxy

private_key = input("private key: ")

proxy = Proxy(private_key, 5000)
proxy.connect()
proxy.get_blockchain()
while True:
    decision = input(
        "What do you want to do?\n 1. Print blockchain\n 2. Mine block\n 3. Create transaction\n 4. Get balance\n 5. get public key\n 6. exit\n"
    )
    if decision == "1":
        print(proxy.blockchain)
    elif decision == "2":
        proxy.mine_block()
    elif decision == "3":
        sender = input("Sender: ")
        receiver = input("Receiver: ")
        amount = float(input("Amount: "))
        proxy.create_transaction(sender, receiver, amount)
    elif decision == "4":
        public_key = input("Public key: ")
        print(proxy.balance(public_key))
    elif decision == "5":
        print(proxy.public_key)
    elif decision == "6":
        break
