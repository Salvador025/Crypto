from __future__ import annotations

import datetime
import hashlib
import json
import threading
from abc import ABC, abstractmethod
from enum import Enum
from typing import List

# cspell: disable-next-line
from ecdsa import SECP256k1, SigningKey


class Transaction(ABC):
    """class for transactions"""

    class Status(Enum):
        """enumeration for transaction status"""

        PENDING = "PENDING"
        CONFIRMED = "CONFIRMED"

    @abstractmethod
    def change_status(self, status: Status) -> None:
        """method to change the status of the transaction"""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """method to return a dictionary with the transaction data"""
        pass


class TransactionUser(Transaction):
    """class for transactions made by users"""

    def __init__(
        self,
        amount: float,
        sender: str,
        receiver: str,
        status: Transaction.Status = Transaction.Status.PENDING,
    ) -> None:
        """constructor method for TransactionUser class"""
        self.__amount: float = amount
        self.__sender: str = sender
        self.__receiver: str = receiver
        self.__status: Transaction.Status = status

    @property
    def amount(self) -> float:
        """getter method for amount"""
        return self.__amount

    @property
    def sender(self) -> str:
        """getter method for sender"""
        return self.__sender

    @property
    def receiver(self) -> str:
        """getter method for receiver"""
        return self.__receiver

    @property
    def status(self) -> Transaction.Status:
        """getter method for status"""
        return self.__status

    def change_status(self, status: Transaction.Status) -> None:
        """method to change the status of the transaction"""
        self.__status = status

    def to_dict(self) -> dict:
        """method to return a dictionary with the transaction data"""
        return {
            "amount": self.amount,
            "sender": self.sender,
            "receiver": self.receiver,
            "status": self.status.value,
        }


class TransactionMiner(Transaction):
    """class for transactions made by miners"""

    def __init__(
        self, amount: float, miner: str, status: Transaction.Status = Transaction.Status.PENDING
    ) -> None:
        """constructor method for TransactionMiner class"""
        self.__reward: float = amount
        self.__miner: str = miner
        self.__coinbase = "ITcoin"
        self.__status: Transaction.Status = status

    @property
    def reward(self) -> float:
        """getter method for amount"""
        return self.__reward

    @property
    def miner(self) -> str:
        """getter method for miner"""
        return self.__miner

    @property
    def coinbase(self) -> str:
        """getter method for coinbase"""
        return self.__coinbase

    @property
    def status(self) -> Transaction.Status:
        """getter method for status"""
        return self.__status

    def change_status(self, status: Transaction.Status) -> None:
        """method to change the status of the transaction"""
        self.__status = status

    def to_dict(self) -> dict:
        """method to return a dictionary with the transaction data"""
        return {
            "amount": self.reward,
            "sender": self.coinbase,
            "receiver": self.miner,
            "status": self.status.value,
        }


class Block:
    """class for blocks"""

    class StatusHolder:
        """class for status holder"""

        def __init__(self) -> None:
            """constructor method for StatusHolder class"""
            self.__status: bool = False

        @property
        def status(self) -> bool:
            """getter method for status"""
            return self.__status

        def Mining(self) -> None:
            """method to change the status to True"""
            self.__status = True

        def NotMining(self) -> None:
            """method to change the status to False"""
            self.__status = False

    def __init__(
        self,
        transactions: List[Transaction],
        timestamp: datetime,
        previous_block: Block = None,
        magic_number: int = 1,
    ) -> None:
        """constructor method for Block class"""
        self.__timestamp: datetime = timestamp
        self.__transactions: List[Transaction] = transactions
        self.__previous_block: Block = previous_block
        self.__magic_number: int = magic_number
        transactions = self.__transaction_to_dict()
        self.__hash: str = self.calculate_hash(transactions, timestamp, self.__magic_number)

    @property
    def timestamp(self) -> datetime:
        """getter method for timestamp"""
        return self.__timestamp

    @property
    def transactions(self) -> List[Transaction]:
        """getter method for transactions"""
        return self.__transactions

    @property
    def previous_block(self) -> str:
        """getter method for previous_hash"""
        return self.__previous_block

    @property
    def hash(self) -> str:
        """getter method for hash"""
        return self.__hash

    def __transaction_to_dict(self) -> list[dict]:
        """method to return a list of dictionaries with the transaction data"""
        transactions = []
        for transaction in self.__transactions:
            transaction = transaction.to_dict()
            transactions.append(
                {
                    "amount": transaction["amount"],
                    "sender": transaction["sender"],
                    "receiver": transaction["receiver"],
                }
            )

        return transactions

    @staticmethod
    def calculate_hash(data: List[Transaction], timestamp: datetime, number: int) -> str:
        """method to calculate the hash of the block"""
        input_data = str(data) + str(timestamp) + str(number)
        input_data = input_data.encode()
        hash = hashlib.sha256(input_data)
        return hash.hexdigest()

    def mine_block(self, difficulty: int, status: StatusHolder) -> bool:
        """method to mine the block"""
        flag = self.__hash[:difficulty] != "0" * difficulty
        while flag and status.status:
            self.__magic_number += 1
            transactions = self.__transaction_to_dict()
            self.__hash = self.calculate_hash(transactions, self.__timestamp, self.__magic_number)
            flag = self.__hash[:difficulty] != "0" * difficulty
        if flag:
            return False
        return True

    def to_dict(self) -> dict:
        """method to return a dictionary with the block data"""
        return {
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "transactions": [transaction.to_dict() for transaction in self.transactions],
            "previous_block": self.previous_block.hash if self.previous_block else None,
            "magic_number": self.__magic_number,
            "hash": self.hash,
        }


class Blockchain:
    """class for blockchain"""

    def __init__(self) -> None:
        """constructor method for Blockchain class"""
        self.__chain: List[Block] = [self.__create_genesis_block()]
        self.__difficulty: int = 4
        self.__mempool: List[Transaction] = []
        self.__mining_reward: int = 10

    @property
    def chain(self) -> List[Block]:
        """getter method for chain"""
        return self.__chain

    @property
    def mempool(self) -> List[Transaction]:
        """getter method for mempool"""
        return self.__mempool

    @property
    def mining_reward(self) -> float:
        """getter method for mining_reward"""
        return self.__mining_reward

    def __create_genesis_block(self) -> Block:
        """method to create the genesis block"""
        return Block([], datetime.datetime.now())

    def get_latest_block(self) -> Block:
        """method to get the latest block"""
        return self.__chain[-1]

    def mine_block(self, public_key: str, status: Block.StatusHolder) -> bool:
        """method to mine pending transactions"""
        block = Block(self.__mempool, datetime.datetime.now(), self.get_latest_block())
        if not block.mine_block(self.__difficulty, status):
            return False
        print("Block successfully mined!")
        for transaction in block.transactions:
            transaction.change_status(Transaction.Status.CONFIRMED)
        self.__chain.append(block)
        self.__mempool = [TransactionMiner(self.__mining_reward, public_key)]
        return True

    def create_transaction(self, sender: str, receiver: str, amount: float) -> None:
        """method to create a transaction"""
        transaction = TransactionUser(amount, sender, receiver)
        self.__mempool.append(transaction)
        return transaction

    # TODO: refactor this method
    def get_balance(self, public_key: str) -> float:
        """method to get the balance of an address"""
        balance = 0
        for block in self.__chain:
            for transaction in block.transactions:
                if transaction.status == Transaction.Status.CONFIRMED:
                    if isinstance(transaction, TransactionUser):
                        if transaction.sender == public_key:
                            balance -= transaction.amount
                        elif transaction.receiver == public_key:
                            balance += transaction.amount
                    elif isinstance(transaction, TransactionMiner):
                        if transaction.miner == public_key:
                            balance += transaction.reward
        return balance

    # TODO: refactor this method
    @staticmethod
    def is_chain_valid(chain: dict) -> bool:
        """method to check if the chain is valid"""
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i - 1]
            transactions = [
                {
                    "amount": transaction["amount"],
                    "sender": transaction["sender"],
                    "receiver": transaction["receiver"],
                }
                for transaction in current_block["transactions"]
            ]
            if current_block["hash"] != Block.calculate_hash(
                transactions,
                datetime.datetime.strptime(current_block["timestamp"], "%Y-%m-%d %H:%M:%S.%f"),
                current_block["magic_number"],
            ):
                return False
            if (
                not current_block["previous_block"]
                or current_block["previous_block"] != previous_block["hash"]
            ):
                return False
        return True

    def __create_transaction(self, transaction_data: dict) -> Transaction:
        """method to create a transaction from a dictionary"""
        if transaction_data["sender"] == "ITcoin":
            transaction = TransactionMiner(
                transaction_data["amount"],
                transaction_data["receiver"],
                Transaction.Status.CONFIRMED
                if transaction_data["status"] == "CONFIRMED"
                else Transaction.Status.PENDING,
            )
        else:
            transaction = TransactionUser(
                transaction_data["amount"],
                transaction_data["sender"],
                transaction_data["receiver"],
                Transaction.Status.CONFIRMED
                if transaction_data["status"] == "CONFIRMED"
                else Transaction.Status.PENDING,
            )
        return transaction

    def __create_transactions(self, transactions_data: dict) -> list[Transaction]:
        """method to create a list of transactions from a dictionary"""
        transactions = []
        for transaction_data in transactions_data:
            transaction = self.__create_transaction(transaction_data)
            transactions.append(transaction)
        return transactions

    def update_chain(self, data: dict) -> None:
        """method to update the chain"""
        self.__chain = []
        previous_block = None
        for block_data in data["chain"]:
            transactions = self.__create_transactions(block_data["transactions"])
            block = Block(
                transactions,
                datetime.datetime.strptime(block_data["timestamp"], "%Y-%m-%d %H:%M:%S.%f"),
                previous_block,
                block_data["magic_number"],
            )
            previous_block = block
            self.__chain.append(block)
        self.__mempool = self.__create_transactions(data["mempool"])

    def update_mempool(self, data: dict) -> None:
        """method to update the mempool"""
        self.__mempool.append(self.__create_transaction(data))

    def generate_key(self, seed_phrase: str) -> str:
        """method to generate public"""
        private_key_bytes = hashlib.sha256(seed_phrase.encode()).digest()
        # cspell: disable-next-line
        sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        vk = sk.verifying_key
        compressed_public_key = vk.to_string("compressed").hex()

        return compressed_public_key

    def to_dict(self) -> dict:
        """method to return a dictionary with the blockchain data"""
        return {
            "chain": [block.to_dict() for block in self.chain],
            "length": len(self.chain),
            "mempool": [transaction.to_dict() for transaction in self.mempool],
        }

    def __str__(self):
        """method to return a string with the blockchain data"""
        return json.dumps(self.to_dict(), indent=4)


if __name__ == "__main__":
    blockchain = Blockchain()
    # cspell: disable-next-line
    public_key1 = blockchain.generate_key("ITAM")
    print("Public key: " + public_key1)
    # cspell: disable-next-line
    public_key2 = blockchain.generate_key("FEWGW")
    print("Public key: " + public_key2)

    blockchain.create_transaction(public_key1, public_key2, 1)
    blockchain.create_transaction(public_key1, public_key2, 2)
    blockchain.create_transaction(public_key1, public_key2, 3)

    status = Block.StatusHolder()
    status.Mining()
    blockchain.mine_block(public_key1, status)
    blockchain.create_transaction(public_key2, public_key1, 2)
    status.Mining()
    blockchain.mine_block(public_key2, status)
    print(blockchain.get_balance(public_key1))
    print(blockchain.get_balance(public_key2))

    blockchain.create_transaction(public_key1, public_key2, 2)
    blockchain.create_transaction(public_key1, public_key2, 3)
    status.Mining()
    blockchain.mine_block(public_key1, status)

    print(blockchain.get_balance(public_key1))
    print(blockchain.get_balance(public_key2))
    print(blockchain)
    print(blockchain.is_chain_valid(blockchain.to_dict()["chain"]))
