
import hashlib
import json
from datetime import datetime


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "data": self.data,
                "previous_hash": self.previous_hash,
            },
            sort_keys=True,
        )
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(
            index=0,
            timestamp=str(datetime.utcnow()),
            data={"event": "GENESIS"},
            previous_hash="0",
        )
        self.chain.append(genesis_block)

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            timestamp=str(datetime.utcnow()),
            data=data,
            previous_hash=previous_block.hash,
        )
        self.chain.append(new_block)
        return new_block

    def get_full_chain(self):
        return self.chain

    def get_blocks_by_kyc_id(self, kyc_id):
        return [
            block for block in self.chain
            if block.data.get("kycId") == kyc_id
        ]

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.compute_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

        return True


# global instance for prototype
blockchain = Blockchain()
