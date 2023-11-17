import threading
from abc import ABC, abstractmethod
from asyncio import sleep

from Blockchain import Block, Blockchain, Transaction
from P2P import P2P


class OperationBlocked(ABC):
    """Interface for the operations that can be done with the blockchain"""

    @abstractmethod
    def get_blockchain(self) -> dict:
        """method to get the blockchain from the network"""
        pass

    @abstractmethod
    def mine_block(self) -> dict:
        """method to mine a block"""
        pass

    @abstractmethod
    def create_transaction(self, sender: str, receiver: str, amount: float) -> Transaction:
        """method to create a transaction"""
        pass

    @abstractmethod
    def balance(self, public_key: str) -> float:
        """method to get the balance of a public key"""
        pass


class OperationP2P(ABC):
    """Interface for the operations that can be done with the P2P network"""

    @abstractmethod
    def connect(self, node: str, public_key: str) -> None:
        """method to connect to a node"""
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """method to validate if the current node is connected to the network"""
        pass


class Proxy(OperationBlocked, OperationP2P):
    """Class that implements the operations that can be done with the blockchain"""

    def __init__(self, private_key: str, port: int = 80) -> None:
        """constructor of the class"""
        self.__blockchain = Blockchain()
        public_key = self.__blockchain.generate_key(private_key)
        self.__p2p = P2P(public_key, self.__blockchain.to_dict(), port, self)

    @property
    def public_key(self) -> str:
        """method to get the public key of the node"""
        return self.__p2p.public_key

    @property
    def blockchain(self) -> Blockchain:
        """method to get the blockchain of the node"""
        return self.__blockchain

    def connect(self) -> None:
        """method to connect to the network"""
        self.__p2p.connect_node()
        self.run()

    def run(self) -> None:
        """method to run the node"""
        threading.Thread(target=self.__p2p.run).start()

    def validate_connection(self) -> bool:
        """method to validate if the node is connected to the network"""
        return self.__p2p.validate_connection()

    def get_blockchain(self) -> None:
        """method to get the blockchain from the network"""
        if not self.validate_connection():
            return
        blockchain = self.__p2p.replace_chain()
        if blockchain == self.__blockchain.to_dict():
            return
        self.__blockchain.update_chain(blockchain)

    def mine_block(self) -> None:
        """method to mine a block"""
        if not self.validate_connection():
            return
        self.__blockchain.mine_block(self.public_key)
        self.__p2p.send_block(self.__blockchain.to_dict())

    def update_blockchain(self, blockchain: dict) -> None:
        """method to update the blockchain"""
        self.__blockchain.update_chain(blockchain)

    def create_transaction(self, sender: str, receiver: str, amount: float) -> Transaction:
        """method to create a transaction"""
        if not self.validate_connection():
            return
        transaction = self.__blockchain.create_transaction(sender, receiver, amount)
        self.__p2p.send_transaction(transaction.to_dict())

    def update_transaction(self, transaction: dict) -> None:
        """method to update the transaction"""
        self.__blockchain.update_mempool(transaction)

    def balance(self, public_key: str) -> float:
        """method to get the balance of a public key"""
        return self.__blockchain.get_balance(public_key)


if __name__ == "__main__":
    proxy = Proxy("private_key", 5000)
    proxy.connect()
    while True:
        input()
        proxy.get_blockchain()
        proxy.create_transaction(
            "03d5d196ef6dbf43704d9866eaf2c3bfa952e168417ca78748967928aa066d9fe3",
            "000095b871bfaa14eeb4cedf7664f5cc13803f5e87b07b1e266f5ecd57fb7e06",
            2,
        )
        proxy.mine_block()
