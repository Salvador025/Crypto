from __future__ import annotations

from typing import List

from Blockchain import Block
from P2P import UsersType
from Proxy import Proxy, Subscriber


class User(Subscriber):
    """class to create a user"""

    def __init__(self, private_key: str, port=80) -> None:
        """constructor of the class"""
        self.__proxy: Proxy = Proxy(private_key, port, self, UsersType.USER)
        self.__public_key: str = self.__proxy.public_key
        self.__proxy.connect()
        self.__proxy.get_blockchain()

    @property
    def public_key(self) -> str:
        """getter method for the public key"""
        return self.__public_key

    @property
    def blockchain(self) -> List[Block]:
        """getter method for the blockchain"""
        return self.__proxy.blockchain

    def get_balance(self) -> float:
        """method to get the balance"""
        return self.__proxy.balance(self.public_key)

    def send_transaction(self, receiver: str, amount: float) -> None:
        """method to send a transaction"""
        self.__proxy.create_transaction(self.__public_key, receiver, amount)

    def stop_connection(self) -> None:
        """method to stop the connection with the network"""
        self.__proxy.stop()

    def update(self, message: dict) -> None:
        """method to update the subscriber"""
        print(f'you received a transaction of {message["amount"]} ITcoins from {message["sender"]}')


class Miner(Subscriber):
    def __init__(self, private_key: str, port=80) -> None:
        """constructor of the class"""
        self.__proxy: Proxy = Proxy(private_key, port, self, UsersType.MINER)
        self.__mining_status: Block.StatusHolder = Block.StatusHolder()
        self.__public_key: str = self.__proxy.public_key
        self.__proxy.connect()
        self.__proxy.get_blockchain()

    @property
    def public_key(self) -> str:
        """getter method for the public key"""
        return self.__public_key

    @property
    def blockchain(self) -> List[Block]:
        """getter method for the blockchain"""
        return self.__proxy.blockchain

    def get_balance(self) -> float:
        """method to get the balance"""
        return self.__proxy.balance(self.public_key)

    def send_transaction(self, receiver: str, amount: float) -> None:
        """method to send a transaction"""
        self.__proxy.create_transaction(self.__public_key, receiver, amount)

    def mine(self) -> None:
        """method to mine a block"""
        self.__mining_status.Mining()
        self.__proxy.mine_block(self.__mining_status)

    def stop_connection(self) -> None:
        """method to stop the node"""
        self.__proxy.stop()

    def update(self, message: str = None) -> None:
        """method to update the subscriber"""
        if message:
            print(
                f'you received a transaction of {message["amount"]} ITcoins from {message["sender"]}'
            )

        self.__mining_status.NotMining()
        print("someone mined a block")


if __name__ == "__main__":
    miner = Miner("MINER", 5000)
    print(miner.blockchain)
    miner.mine()
