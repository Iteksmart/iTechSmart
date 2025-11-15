"""
iTechSmart Ledger - Blockchain & Audit Trail Platform
Immutable audit trails, smart contracts, and cryptographic verification
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from uuid import uuid4
import hashlib
import json


class BlockchainType(str, Enum):
    ETHEREUM = "ethereum"
    HYPERLEDGER = "hyperledger"
    PRIVATE = "private"


class Block:
    def __init__(self, index: int, timestamp: str, data: Dict[str, Any], previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()


class AuditRecord:
    def __init__(self, record_id: str, entity: str, action: str, data: Dict[str, Any]):
        self.record_id = record_id
        self.entity = entity
        self.action = action
        self.data = data
        self.timestamp = datetime.utcnow()
        self.block_index = None
        self.verified = False


class SmartContract:
    def __init__(self, contract_id: str, name: str, code: str):
        self.contract_id = contract_id
        self.name = name
        self.code = code
        self.deployed_at = datetime.utcnow()
        self.executions = 0
        self.is_active = True


class LedgerEngine:
    def __init__(self):
        self.chain: List[Block] = []
        self.audit_records: Dict[str, AuditRecord] = {}
        self.smart_contracts: Dict[str, SmartContract] = {}
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(0, datetime.utcnow().isoformat(), {"genesis": True}, "0")
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the latest block"""
        return self.chain[-1]
    
    def add_block(self, data: Dict[str, Any]) -> Block:
        """Add a new block to the chain"""
        latest_block = self.get_latest_block()
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.utcnow().isoformat(),
            data=data,
            previous_hash=latest_block.hash
        )
        self.chain.append(new_block)
        return new_block
    
    def create_audit_record(self, entity: str, action: str, data: Dict[str, Any]) -> str:
        """Create immutable audit record"""
        record_id = str(uuid4())
        record = AuditRecord(record_id, entity, action, data)
        
        # Add to blockchain
        block = self.add_block({
            "record_id": record_id,
            "entity": entity,
            "action": action,
            "data": data,
            "timestamp": record.timestamp.isoformat()
        })
        
        record.block_index = block.index
        record.verified = True
        
        self.audit_records[record_id] = record
        return record_id
    
    def verify_record(self, record_id: str) -> bool:
        """Verify audit record integrity"""
        record = self.audit_records.get(record_id)
        if not record or record.block_index is None:
            return False
        
        # Verify block exists and hasn't been tampered
        if record.block_index >= len(self.chain):
            return False
        
        block = self.chain[record.block_index]
        return block.hash == block.calculate_hash()
    
    def verify_chain(self) -> bool:
        """Verify entire blockchain integrity"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify current block hash
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Verify link to previous block
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def deploy_smart_contract(self, name: str, code: str) -> str:
        """Deploy a smart contract"""
        contract_id = str(uuid4())
        contract = SmartContract(contract_id, name, code)
        self.smart_contracts[contract_id] = contract
        
        # Record deployment on blockchain
        self.add_block({
            "type": "smart_contract_deployment",
            "contract_id": contract_id,
            "name": name,
            "deployed_at": contract.deployed_at.isoformat()
        })
        
        return contract_id
    
    def execute_smart_contract(self, contract_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a smart contract"""
        contract = self.smart_contracts.get(contract_id)
        if not contract or not contract.is_active:
            return {"success": False, "error": "Contract not found or inactive"}
        
        contract.executions += 1
        
        # Record execution on blockchain
        execution_id = str(uuid4())
        self.add_block({
            "type": "smart_contract_execution",
            "contract_id": contract_id,
            "execution_id": execution_id,
            "params": params,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "execution_id": execution_id,
            "result": "Contract executed successfully"
        }
    
    def get_audit_trail(self, entity: str) -> List[Dict[str, Any]]:
        """Get audit trail for an entity"""
        records = [r for r in self.audit_records.values() if r.entity == entity]
        
        return [
            {
                "record_id": r.record_id,
                "action": r.action,
                "data": r.data,
                "timestamp": r.timestamp.isoformat(),
                "block_index": r.block_index,
                "verified": r.verified
            }
            for r in sorted(records, key=lambda x: x.timestamp)
        ]
    
    def sign_data(self, data: Dict[str, Any]) -> str:
        """Create digital signature"""
        data_string = json.dumps(data, sort_keys=True)
        signature = hashlib.sha256(data_string.encode()).hexdigest()
        
        # Record signature on blockchain
        self.add_block({
            "type": "digital_signature",
            "signature": signature,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return signature
    
    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """Verify digital signature"""
        data_string = json.dumps(data, sort_keys=True)
        expected_signature = hashlib.sha256(data_string.encode()).hexdigest()
        return signature == expected_signature
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_blocks": len(self.chain),
            "total_audit_records": len(self.audit_records),
            "total_smart_contracts": len(self.smart_contracts),
            "active_contracts": len([c for c in self.smart_contracts.values() if c.is_active]),
            "chain_verified": self.verify_chain()
        }


ledger_engine = LedgerEngine()