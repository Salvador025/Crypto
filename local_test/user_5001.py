import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Subscriber import User

private_key = input("private key: ")
try:
    user = User(private_key, 5001)
    while True:
        decision = input(
            "What do you want to do?\n 1. Print blockchain\n 2. Create transaction\n 3. Get balance\n 4. get public key\n 5. exit\n"
        )
        if decision == "1":
            print(user.blockchain)
        elif decision == "2":
            receiver = input("Receiver: ")
            amount = float(input("Amount: "))
            user.send_transaction(receiver, amount)
        elif decision == "3":
            print(user.get_balance())
        elif decision == "4":
            print(user.public_key)
        elif decision == "5":
            user.stop()
            break
except KeyboardInterrupt:
    user.stop()
