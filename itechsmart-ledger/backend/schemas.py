from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class BlockchainNetwork(str, Enum):
    ETHEREUM = "ethereum"
    BITCOIN = "bitcoin"
    POLYGON = "polygon"
    BINANCE = "binance"
    SOLANA = "solana"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WalletType(str, Enum):
    HOT = "hot"
    COLD = "cold"
    MULTISIG = "multisig"

class ContractStatus(str, Enum):
    DRAFT = "draft"
    DEPLOYED = "deployed"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Wallet Schemas
class WalletBase(BaseModel):
    name: str
    network: BlockchainNetwork
    wallet_type: WalletType = WalletType.HOT

class WalletCreate(WalletBase):
    pass

class WalletImport(WalletBase):
    private_key: str

class WalletResponse(WalletBase):
    id: int
    user_id: int
    address: str
    balance: float
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Transaction Schemas
class TransactionBase(BaseModel):
    to_address: str
    network: BlockchainNetwork
    amount: float
    metadata: Optional[Dict[str, Any]] = None

class TransactionCreate(TransactionBase):
    from_wallet_id: int
    gas_price: Optional[float] = None
    gas_limit: Optional[int] = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    from_wallet_id: Optional[int]
    to_wallet_id: Optional[int]
    from_address: Optional[str]
    fee: float
    transaction_hash: Optional[str]
    block_number: Optional[int]
    status: TransactionStatus
    confirmations: int
    created_at: datetime
    confirmed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Smart Contract Schemas
class SmartContractBase(BaseModel):
    name: str
    description: Optional[str] = None
    network: BlockchainNetwork

class SmartContractCreate(SmartContractBase):
    source_code: str
    compiler_version: Optional[str] = "0.8.0"

class SmartContractDeploy(BaseModel):
    contract_id: int
    constructor_params: Optional[List[Any]] = []
    gas_limit: Optional[int] = None

class SmartContractResponse(SmartContractBase):
    id: int
    user_id: int
    contract_address: Optional[str]
    status: ContractStatus
    is_verified: bool
    created_at: datetime
    deployed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Contract Interaction Schemas
class ContractInteractionCreate(BaseModel):
    contract_id: int
    function_name: str
    parameters: List[Any] = []

class ContractInteractionResponse(BaseModel):
    id: int
    contract_id: int
    user_id: int
    function_name: str
    parameters: List[Any]
    transaction_hash: Optional[str]
    status: TransactionStatus
    gas_used: Optional[int]
    result: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Block Schemas
class BlockResponse(BaseModel):
    id: int
    network: BlockchainNetwork
    block_number: int
    block_hash: str
    parent_hash: Optional[str]
    timestamp: datetime
    miner: Optional[str]
    transaction_count: int
    gas_used: Optional[int]
    gas_limit: Optional[int]
    
    class Config:
        from_attributes = True

# Token Schemas
class TokenBase(BaseModel):
    network: BlockchainNetwork
    contract_address: str
    name: str
    symbol: str
    decimals: int = 18

class TokenCreate(TokenBase):
    token_type: str = "ERC20"
    logo_url: Optional[str] = None

class TokenResponse(TokenBase):
    id: int
    total_supply: Optional[str]
    token_type: str
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token Balance Schemas
class TokenBalanceResponse(BaseModel):
    id: int
    wallet_id: int
    token_id: int
    balance: str
    last_updated: datetime
    token: TokenResponse
    
    class Config:
        from_attributes = True

# Network Config Schemas
class NetworkConfigBase(BaseModel):
    network: BlockchainNetwork
    rpc_url: str
    chain_id: Optional[int] = None
    explorer_url: Optional[str] = None
    is_testnet: bool = False

class NetworkConfigCreate(NetworkConfigBase):
    pass

class NetworkConfigUpdate(BaseModel):
    rpc_url: Optional[str] = None
    is_active: Optional[bool] = None
    gas_price_multiplier: Optional[float] = None

class NetworkConfigResponse(NetworkConfigBase):
    id: int
    is_active: bool
    gas_price_multiplier: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# API Key Schemas
class APIKeyCreate(BaseModel):
    name: str
    rate_limit: int = 1000
    allowed_networks: Optional[List[BlockchainNetwork]] = None
    expires_at: Optional[datetime] = None

class APIKeyResponse(BaseModel):
    id: int
    user_id: int
    name: str
    key: str
    is_active: bool
    rate_limit: int
    allowed_networks: Optional[List[str]]
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Analytics Schemas
class NetworkStats(BaseModel):
    network: BlockchainNetwork
    total_transactions: int
    total_wallets: int
    total_volume: float
    avg_transaction_fee: float

class DashboardStats(BaseModel):
    total_wallets: int
    total_transactions: int
    total_smart_contracts: int
    total_volume: float
    network_stats: List[NetworkStats]

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    username: str
    password: str