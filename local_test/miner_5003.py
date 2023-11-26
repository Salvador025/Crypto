import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Subscriber import Miner

private_key = input("private key: ")

miner = Miner(private_key, 5003)
while True:
    decision = input(
        "What do you want to do?\n 1. Print blockchain\n 2. Create transaction\n 3. Get balance\n 4. get public key\n 5. mine block\n 6. exit\n"
    )
    if decision == "1":
        print(miner.blockchain)
    elif decision == "2":
        receiver = input("Receiver: ")
        amount = float(input("Amount: "))
        miner.send_transaction(receiver, amount)
    elif decision == "3":
        print(miner.get_balance())
    elif decision == "4":
        print(miner.public_key)
    elif decision == "5":
        miner.mine()
    elif decision == "6":
        break
