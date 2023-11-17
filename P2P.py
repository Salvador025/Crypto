import socket

import requests
from Blockchain import Blockchain
from flask import Flask, request


class P2P:
    def __init__(self, public_key: str, blockchain: dict, port: int = 80, proxy=None):
        """P2P class constructor"""
        self.__proxy = proxy
        self.__public_key: str = public_key
        self.__blockchain: dict = blockchain
        self.__port: int = port
        self.app = Flask(__name__)
        self.__nodes = set()

    @property
    def public_key(self) -> str:
        return self.__public_key

    def connect_node(self):
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

    def add_node(self, node, public_key):
        """method to add a node to the network"""
        dict_node = {"url": node, "public_key": public_key}
        self.__nodes.add(tuple(dict_node.items()))

    def replace_chain(self):
        """method to replace the current blockchain with the longest blockchain in the network"""
        network = self.__nodes
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
                if length > max_length and Blockchain.is_chain_valid(blockchain["chain"]):
                    max_length = length
                    longest_blockchain = blockchain
        if longest_blockchain:
            self.__blockchain = longest_blockchain
        return self.__blockchain

    def send_block(self, chain: dict):
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

    def send_transaction(self, transaction: dict):
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

    def validate_connection(self):
        """method to validate if the current node is connected to the network"""
        if not self.__nodes:
            return False

        current_node = {
            "url": f"{socket.gethostbyname(socket.gethostname())}:{self.__port}",
            "public_key": self.__public_key,
        }
        for node in self.__nodes:
            node_dict = dict(node)
            if node_dict != current_node:
                return True
        return False

    def get_network(self):
        @self.app.route("/get_network", methods=["GET"])
        def get_network_route():
            """method to get the network"""
            headers = request.headers
            public_keys = [
                item[1]
                for sub_tupla in self.__nodes
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

    def get_blockchain(self):
        @self.app.route("/get_blockchain", methods=["GET"])
        def get_blockchain_route():
            """method to get the blockchain"""
            headers = request.headers

            public_keys = [
                item[1]
                for sub_tupla in self.__nodes
                for item in sub_tupla
                if item[0] == "public_key"
            ]
            if headers["key"] not in public_keys:
                self.add_node(f"{request.remote_addr}:{headers['port']}", headers["key"])
            return self.__blockchain

    def receive_blockchain(self):
        @self.app.route("/receive_blockchain", methods=["POST"])
        def receive_blockchain_route():
            """method to receive the blockchain"""
            if self.__blockchain["length"] < request.json["length"] and Blockchain.is_chain_valid(
                request.json["chain"]
            ):
                self.__blockchain = request.json
                if self.__proxy:
                    self.__proxy.update_blockchain(self.__blockchain)
                print("blockchain received")
                return "blockchain received"
            return "blockchain rejected"

    def receive_transaction(self):
        @self.app.route("/receive_transaction", methods=["POST"])
        def receive_transaction_route():
            """method to receive a transaction"""
            transaction = request.json
            self.__blockchain["mempool"].append(transaction)
            if self.__proxy:
                self.__proxy.update_transaction(transaction)
            print("transaction received")
            return "transaction received"

    def run(self):
        """method to run the server"""
        self.get_blockchain()
        self.receive_blockchain()
        self.get_network()
        self.receive_transaction()
        # cspell: disable-next-line
        local_ip = socket.gethostbyname(socket.gethostname())
        self.add_node(node=f"{local_ip}:{self.__port}", public_key=self.__public_key)
        self.app.run(host="0.0.0.0", port=self.__port)


if __name__ == "__main__":
    blockchain = Blockchain()
    # cspell: disable-next-line
    public_key1 = blockchain.generate_key("ITAM")
    print(public_key1)
    # cspell: disable-next-line
    public_key2 = blockchain.generate_key("FEWGW")
    print(public_key2)

    blockchain.create_transaction(public_key1, public_key2, 1)
    blockchain.create_transaction(public_key1, public_key2, 2)
    blockchain.create_transaction(public_key1, public_key2, 3)

    blockchain.mine_block(public_key1)
    blockchain.create_transaction(public_key2, public_key1, 2)
    blockchain.mine_block(public_key2)
    p2p = P2P("server", blockchain.to_dict())
    p2p.run()
