import socket
import threading
from enum import Enum
from typing import Set, Tuple
from wsgiref.simple_server import make_server

import requests
from Blockchain import Blockchain
from flask import Flask, request


class UsersType(Enum):
    """enum to manage the type of user"""

    SERVER = "server"
    USER = "user"
    MINER = "miner"


class P2P:
    """class to manage the peer to peer network"""

    def __init__(
        self,
        public_key: str,
        blockchain: dict,
        port: int = 80,
        proxy=None,
        type: UsersType = UsersType.SERVER,
    ):
        """P2P class constructor"""
        self.__proxy = proxy
        self.__public_key: str = public_key
        self.__blockchain: dict = blockchain
        self.__port: int = port
        self.__app: Flask = Flask(__name__)
        self.__nodes: Set[Tuple[str, str]] = set()
        self.__type: UsersType = type
        self.__server = None

    @property
    def public_key(self) -> str:
        return self.__public_key

    def connect_node(self) -> None:
        """method to connect to node in the network and receive the blockchain"""
        headers = {
            "Content-Type": "application/json",
            "key": str(self.__public_key),
            "port": str(self.__port),
        }
        response = requests.get("http://127.0.0.1:80/get_network", headers=headers)
        if response.status_code == 200:
            nodes = response.json()
            for node in nodes:
                node = dict(node)
                self.add_node(node["url"], node["public_key"])

    def add_node(self, node: str, public_key: str) -> None:
        """method to add a node to the network"""
        dict_node = {"url": node, "public_key": public_key}
        self.__nodes.add(tuple(dict_node.items()))

    # TODO refactor this method
    def replace_chain(self) -> dict:
        """method to replace the current blockchain with the longest blockchain in the network"""
        network = tuple(self.__nodes)
        longest_blockchain = self.__blockchain
        max_length = self.__blockchain["length"]
        for node in network:
            node_dict = dict(node)
            headers = {
                "Content-Type": "application/json",
                "port": str(self.__port),
                "key": str(self.__public_key),
            }
            if node_dict["public_key"] == self.__public_key:
                continue
            url = node_dict["url"]
            response = requests.get(f"http://{url}/get_blockchain", headers=headers)
            if response.status_code == 200:
                length = response.json()["length"]
                blockchain = response.json()
                if Blockchain.is_chain_valid(blockchain["chain"]):
                    if length > max_length or (
                        length == max_length
                        and len(blockchain["mempool"]) > len(longest_blockchain["mempool"])
                    ):
                        max_length = length
                        longest_blockchain = blockchain
        if longest_blockchain:
            self.__blockchain = longest_blockchain
        return self.__blockchain

    def send_block(self, chain: dict) -> None:
        """method to send the current blockchain to the network"""
        self.__blockchain = chain
        network = self.__nodes
        for node in network:
            node_dict = dict(node)
            url = node_dict["url"]
            if node_dict["public_key"] == self.__public_key:
                continue
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"http://{url}/receive_blockchain", json=self.__blockchain, headers=headers
            )
            if response.status_code == 200:
                print("blockchain sent")

    def send_transaction(self, transaction: dict) -> None:
        """method to send a transaction to the network"""
        network = self.__nodes
        for node in network:
            node_dict = dict(node)
            url = node_dict["url"]
            if node_dict["public_key"] == self.__public_key:
                continue
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"http://{url}/receive_transaction", json=transaction, headers=headers
            )
            if response.status_code == 200:
                pass

    def validate_connection(self) -> bool:
        """method to validate if the current node is connected to the network"""
        if not self.__nodes:
            return False

        current_node = {
            # cspell: disable-next-line
            "url": f"{socket.gethostbyname(socket.gethostname())}:{self.__port}",
            "public_key": self.__public_key,
        }
        for node in self.__nodes:
            node_dict = dict(node)
            if node_dict != current_node:
                return True
        return False

    def get_network(self) -> None:
        """method to get the network"""

        @self.__app.route("/get_network", methods=["GET"])
        def get_network_route() -> dict:
            """route to get the network"""
            headers = request.headers
            public_keys = [
                item[1]
                # cspell: disable-next-line
                for sub_tupla in self.__nodes
                # cspell: disable-next-line
                for item in sub_tupla
                if item[0] == "public_key"
            ]
            if headers["key"] not in public_keys:
                self.add_node(f"{request.remote_addr}:{headers['port']}", headers["key"])

            data = []
            for tuple_node in self.__nodes:
                dict_node = dict(tuple_node)
                data.append(dict_node)
            return data

    def get_blockchain(self) -> None:
        """method to get the blockchain"""

        @self.__app.route("/get_blockchain", methods=["GET"])
        def get_blockchain_route() -> dict:
            """route to get the blockchain"""
            headers = request.headers

            public_keys = [
                item[1]
                # cspell: disable-next-line
                for sub_tupla in self.__nodes
                # cspell: disable-next-line
                for item in sub_tupla
                if item[0] == "public_key"
            ]
            if headers["key"] not in public_keys:
                self.add_node(f"{request.remote_addr}:{headers['port']}", headers["key"])
            return self.__blockchain

    def receive_blockchain(self) -> None:
        """method to receive the blockchain"""

        @self.__app.route("/receive_blockchain", methods=["POST"])
        def receive_blockchain_route() -> str:
            """route to receive the blockchain"""
            if self.__blockchain["length"] < request.json["length"] and Blockchain.is_chain_valid(
                request.json["chain"]
            ):
                self.__blockchain = request.json
                if self.__proxy:
                    self.__proxy.update_blockchain(self.__blockchain)
                    if self.__type == UsersType.MINER:
                        self.__proxy.notify()
                print("blockchain received")
                return "blockchain received"
            return "blockchain rejected"

    def receive_transaction(self) -> None:
        @self.__app.route("/receive_transaction", methods=["POST"])
        def receive_transaction_route() -> str:
            """route to receive a transaction"""
            transaction = request.json
            self.__blockchain["mempool"].append(transaction)
            if self.__proxy:
                self.__proxy.update_transaction(transaction)
                if self.__type == UsersType.USER or self.__type == UsersType.MINER:
                    if self.__public_key == transaction["receiver"]:
                        self.__proxy.notify(transaction)
            return "transaction received"

    def disconnect_node(self) -> None:
        """method to disconnect a node from the network"""

        @self.__app.route("/disconnect_node", methods=["DELETE"])
        def disconnect_node_route() -> str:
            """route to disconnect a node from the network"""
            headers = request.headers
            public_key_to_remove = headers["key"]
            node_to_remove = None

            # Find the tuple that contains the public key to remove
            for node in self.__nodes:
                if dict(node).get("public_key") == public_key_to_remove:
                    node_to_remove = node
                    break

            # If the node is found, remove it from the set
            if node_to_remove:
                self.__nodes.remove(node_to_remove)
                return "node disconnected"
            else:
                return "node not found"

    # TODO refactor this method
    def stop(self) -> None:
        """method to stop the server"""
        network = tuple(self.__nodes)
        for node in network:
            node_dict = dict(node)
            headers = {
                "Content-Type": "application/json",
                "port": str(self.__port),
                "key": str(self.__public_key),
            }
            if node_dict["public_key"] == self.__public_key:
                continue
            url = node_dict["url"]

            response = requests.delete(f"http://{url}/disconnect_node", headers=headers)
            if response.status_code == 200:
                print("node disconnected")

        if self.__server:
            self.__server.shutdown()
            self.flask_thread.join()

    def run(self) -> None:
        """method to run the server"""

        def flask_thread():
            """method to run the server in a thread"""
            self.__app = Flask(__name__)
            self.get_blockchain()
            self.receive_blockchain()
            self.get_network()
            self.receive_transaction()
            self.disconnect_node()
            # cspell: disable-next-line
            local_ip = socket.gethostbyname(socket.gethostname())
            self.add_node(node=f"{local_ip}:{self.__port}", public_key=self.__public_key)
            self.__server = make_server("0.0.0.0", self.__port, self.__app)
            self.__server.serve_forever()

        self.flask_thread = threading.Thread(target=flask_thread)
        self.flask_thread.start()
