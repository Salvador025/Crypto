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
        -mempool: Transaction[]
        -difficulty: int
        -mine_reward: int
        -create_genesis_block(): Block
        +last_block(): Block
        +mine_block()
        +is_chain_valid(): bool
        +create_transaction(sender:str,receiver, amount)
        +get_balance(public_key): float
        +generate_key(): string
        +to_dict(): dict
    }

    class P2P{
        -public_key: string
        -host: string
        -port: int
        -network: dict[string, string]
        +connect(public_key)
        +send_blockchain(blockchain: Blockchain)
        +receive_blockchain(): Blockchain
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
        +mine_block(difficulty: int)
        +to_dict(): dict
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
        -receiver
        -amount
        -status
        +change_status(status: Status)
        +to_dict(): dict
    }

    class TransactionMiner{
        -miner
        -reward
        -status
        -coinbase
        -status
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
