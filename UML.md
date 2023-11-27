# UML

SSH key generation
```mermaid
classDiagram

    class OperationsP2P{
        <<interface>>
        +connect(public_key)
        +send_blockchain(blockchain: Blockchain)
        +receive_blockchain(): Blockchain
    }

    class OperationsBlockchain{
        <<interface>>
        +get_blockchain(): Blockchain
        +mine_block()
        +create_transaction(): Transaction
        +balance(public_key): float
        +generate_key(): string
    }
    
    class Proxy{
        -Blockchain: Blockchain
        -P2P: P2P
        -miners: Miner[]
        -users: User[]
        +validate_key():bool
        +validate_connection():bool
        +get_blockchain(): Blockchain
        +mine_block()
        +create_transaction(): Transaction
        +balance(): float
        +generate_key(): string
        +create_transaction(): Transaction
        +connect(public_key)
        +send_blockchain(blockchain: Blockchain)
        +receive_blockchain(): Blockchain
    }

    class Blockchain{
        -chain: Block[]
        -difficulty: int
        -mempool: Transaction[]
        -mine_reward: int
        -create_genesis_block(): Block
        +last_block(): Block
        +mine_block(public_key: string, status: StatusHolder): bool
        +create_transaction(sender:str,receiver: str, amount: float)
        +get_balance(public_key: str): float
        +is_chain_valid(chain: dict): bool
        -create_transaction(transaction_data: dict): Transaction
        -create_transactions(transactions_data: dict): Transaction[]
        +update_chain(data: dict)
        +update_mempool(data: dict)
        +generate_key(seed_phrase: string): string
        +to_dict(): dict
    }

<!--checking  -->
    class P2P{
        -proxy: Proxy
        -public_key: string
        -blockchain: dict
        -port: int
        +app: Flask
        -nodes: Set[(url: string, public_key: string)]
        +connect(public_key)
        +send_blockchain(blockchain: Blockchain)
        +receive_blockchain(): Blockchain
    }

    class UsersType{
        <<enum>>
        +SERVER
        +USER
        +MINER
    }

    class Subscriber{
        <<interface>>
        +update()
    }

    class Miner{
        +Proxy: Proxy
        +mine_block()
        +update()
    }

    class User{
        +Proxy: Proxy
        +update()
    }

    class Block{
        -timestamp: datetime
        -transactions: Transactions[]
        -previous_block: Block
        -magic_number: int
        -hash: string
        +calculate_hash(data: Transactions[], timestamp: datetime, number: int): string
        +mine_block(difficulty: int, status: StatusHolder): bool
        +to_dict(): dict
    }

    class StatusHolder{
        -status: bool
        Mining() : bool
        NotMining() : bool
    }

    class Transaction{
        <<interface>>
        +change_status(status: Status)
        +to_dict(): dict
    }

    class Status{
        <<enum>>
        +PENDING
        +CONFIRMED
    }

    class TransactionUser{
        -sender
        -amount: float
        -receiver: string
        -status: Status
        +change_status(status: Status)
        +to_dict(): dict
    }

    class TransactionMiner{
        -reward: float
        -miner: string
        -coinbase: string
        -status: Status
        +change_status(status: Status)
        +to_dict(): dict
    }

    

    

    Blockchain o--> Block
    Transaction <--o Block
    Blockchain o--> Transaction
    Transaction <|.. Status  
    Transaction ..|> TransactionUser
    Transaction ..|> TransactionMiner
    Proxy *--> Blockchain
    OperationsBlockchain <|..Proxy 
    Blockchain ..> Transaction
    Proxy *--> P2P
    OperationsP2P <|.. Proxy 
    Proxy *--> Subscriber
    User ..|> Subscriber  
    Miner ..|> Subscriber
    Proxy <-- Miner
    Proxy <-- User

```
