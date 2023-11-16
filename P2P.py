import requests
from Blockchain import Blockchain
from flask import Flask, request


class P2P:
    def __init__(self, public_key: str, blockchain: dict, port: int = 80):
        self.public_key: str = public_key
        self.blockchain: dict = blockchain
        self.port: int = port
        self.app = Flask(__name__)
        self.nodes = set()

    def connect_node(self):
        headers = {
            "Content-Type": "application/json",
            "key": str(self.public_key),
            "port": str(self.port),
        }
        response = requests.get("http://127.0.0.1:80/get_network", headers=headers)
        if response.status_code == 200:
            nodes = response.json()
            for node in nodes:
                node = dict(node)
                self.add_node(node["url"], node["public_key"])

    def add_node(self, node, public_key):
        # cspell: disable-next-line
        # cspell: disable-next-line
        dict_node = {"url": node, "public_key": public_key}
        self.nodes.add(tuple(dict_node.items()))

    def replace_chain(self):
        network = self.nodes
        longest_blockchain = self.blockchain
        max_length = self.blockchain["length"]
        for node in network:
            node_dict = dict(node)
            headers = {
                "Content-Type": "application/json",
                "port": str(self.port),
                "key": str(self.public_key),
            }
            if node_dict["public_key"] == self.public_key:
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
            self.blockchain = longest_blockchain
        return self.blockchain

    def send_block(self, chain: dict):
        self.blockchain = chain
        network = self.nodes
        for node in network:
            node_dict = dict(node)
            url = node_dict["url"]
            if node_dict["public_key"] == self.public_key:
                continue
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"http://{url}/receive_blockchain", json=self.blockchain, headers=headers
            )
            if response.status_code == 200:
                pass

    def send_transaction(self, transaction: dict):
        network = self.nodes
        for node in network:
            node_dict = dict(node)
            url = node_dict["url"]
            if node_dict["public_key"] == self.public_key:
                continue
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"http://{url}/receive_transaction", json=transaction, headers=headers
            )
            if response.status_code == 200:
                pass

    def get_network(self):
        @self.app.route("/get_network", methods=["GET"])
        def get_network_route():
            headers = request.headers
            public_keys = [
                item[1] for sub_tupla in self.nodes for item in sub_tupla if item[0] == "public_key"
            ]
            if headers["key"] not in public_keys:
                self.add_node(f"{request.remote_addr}:{headers['port']}", headers["key"])

            data = []
            for tuple_node in self.nodes:
                dict_node = dict(tuple_node)
                data.append(dict_node)
            return data

    def get_blockchain(self):
        @self.app.route("/get_blockchain", methods=["GET"])
        def get_blockchain_route():
            headers = request.headers

            public_keys = [
                item[1] for sub_tupla in self.nodes for item in sub_tupla if item[0] == "public_key"
            ]
            if headers["key"] not in public_keys:
                self.add_node(f"{request.remote_addr}:{headers['port']}", headers["key"])
            return self.blockchain

    def receive_blockchain(self):
        @self.app.route("/receive_blockchain", methods=["POST"])
        def receive_blockchain_route():
            if self.blockchain["length"] < request.json["length"] and Blockchain.is_chain_valid(
                request.json["chain"]
            ):
                self.blockchain = request.json
                return "blockchain received"
            return "blockchain rejected"

    def receive_transaction(self):
        @self.app.route("/receive_transaction", methods=["POST"])
        def receive_transaction_route():
            self.blockchain["mempool"].append(request.json)
            return "transaction received"

    def run(self):
        self.get_blockchain()
        self.receive_blockchain()
        self.get_network()
        self.receive_transaction()
        self.app.run(host="0.0.0.0", port=self.port)


if __name__ == "__main__":
    blockchain = Blockchain()
    # cspell: disable-next-line
    public_key1 = blockchain.generate_key("ITAM")
    # cspell: disable-next-line
    public_key2 = blockchain.generate_key("FEWGW")

    blockchain.create_transaction(public_key1, public_key2, 1)
    blockchain.create_transaction(public_key1, public_key2, 2)
    blockchain.create_transaction(public_key1, public_key2, 3)

    blockchain.mine_block(public_key1)
    blockchain.create_transaction(public_key2, public_key1, 2)
    blockchain.mine_block(public_key2)
    p2p = P2P("server", blockchain.to_dict())
    p2p.add_node("127.0.0.1:80", "server")
    p2p.run()
