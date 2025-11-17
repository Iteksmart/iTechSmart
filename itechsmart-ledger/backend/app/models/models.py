from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum


class BlockchainNetwork(str, enum.Enum):
    ETHEREUM = "ethereum"
    BITCOIN = "bitcoin"
    POLYGON = "polygon"
    BINANCE = "binance"
    SOLANA = "solana"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WalletType(str, enum.Enum):
    HOT = "hot"
    COLD = "cold"
    MULTISIG = "multisig"


class ContractStatus(str, enum.Enum):
    DRAFT = "draft"
    DEPLOYED = "deployed"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"


# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    wallets = relationship("Wallet", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    smart_contracts = relationship("SmartContract", back_populates="user")


# Wallet Model
class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(String(255), unique=True, index=True, nullable=False)
    network = Column(SQLEnum(BlockchainNetwork), nullable=False)
    wallet_type = Column(SQLEnum(WalletType), default=WalletType.HOT)
    balance = Column(Float, default=0.0)
    encrypted_private_key = Column(Text)  # Encrypted storage
    public_key = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="wallets")
    sent_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.from_wallet_id",
        back_populates="from_wallet",
    )
    received_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.to_wallet_id",
        back_populates="to_wallet",
    )


# Transaction Model
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    from_wallet_id = Column(Integer, ForeignKey("wallets.id"))
    to_wallet_id = Column(Integer, ForeignKey("wallets.id"))
    from_address = Column(String(255), index=True)
    to_address = Column(String(255), index=True, nullable=False)
    network = Column(SQLEnum(BlockchainNetwork), nullable=False)
    amount = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)
    gas_price = Column(Float)
    gas_limit = Column(Integer)
    nonce = Column(Integer)
    transaction_hash = Column(String(255), unique=True, index=True)
    block_number = Column(Integer)
    block_hash = Column(String(255))
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    confirmations = Column(Integer, default=0)
    metadata = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="transactions")
    from_wallet = relationship(
        "Wallet", foreign_keys=[from_wallet_id], back_populates="sent_transactions"
    )
    to_wallet = relationship(
        "Wallet", foreign_keys=[to_wallet_id], back_populates="received_transactions"
    )


# Smart Contract Model
class SmartContract(Base):
    __tablename__ = "smart_contracts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    network = Column(SQLEnum(BlockchainNetwork), nullable=False)
    contract_address = Column(String(255), unique=True, index=True)
    abi = Column(JSON)
    bytecode = Column(Text)
    source_code = Column(Text)
    compiler_version = Column(String(50))
    status = Column(SQLEnum(ContractStatus), default=ContractStatus.DRAFT)
    deployment_transaction = Column(String(255))
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    deployed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="smart_contracts")
    interactions = relationship("ContractInteraction", back_populates="contract")


# Contract Interaction Model
class ContractInteraction(Base):
    __tablename__ = "contract_interactions"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("smart_contracts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    function_name = Column(String(255), nullable=False)
    parameters = Column(JSON)
    transaction_hash = Column(String(255), index=True)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    gas_used = Column(Integer)
    result = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    contract = relationship("SmartContract", back_populates="interactions")


# Block Model
class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    network = Column(SQLEnum(BlockchainNetwork), nullable=False)
    block_number = Column(Integer, nullable=False, index=True)
    block_hash = Column(String(255), unique=True, index=True, nullable=False)
    parent_hash = Column(String(255))
    timestamp = Column(DateTime, nullable=False)
    miner = Column(String(255))
    difficulty = Column(String(100))
    total_difficulty = Column(String(100))
    size = Column(Integer)
    gas_used = Column(Integer)
    gas_limit = Column(Integer)
    transaction_count = Column(Integer, default=0)
    extra_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# Token Model
class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    network = Column(SQLEnum(BlockchainNetwork), nullable=False)
    contract_address = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    symbol = Column(String(50), nullable=False)
    decimals = Column(Integer, default=18)
    total_supply = Column(String(100))
    token_type = Column(String(50))  # ERC20, ERC721, ERC1155, etc.
    logo_url = Column(String(500))
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Token Balance Model
class TokenBalance(Base):
    __tablename__ = "token_balances"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    balance = Column(String(100), default="0")
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Network Configuration Model
class NetworkConfig(Base):
    __tablename__ = "network_configs"

    id = Column(Integer, primary_key=True, index=True)
    network = Column(SQLEnum(BlockchainNetwork), unique=True, nullable=False)
    rpc_url = Column(String(500), nullable=False)
    chain_id = Column(Integer)
    explorer_url = Column(String(500))
    is_testnet = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    gas_price_multiplier = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# API Key Model
class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    key = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=1000)
    allowed_networks = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)


# Audit Log Model
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
