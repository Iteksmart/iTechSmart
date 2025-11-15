from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
from passlib.context import CryptContext
from jose import JWTError, jwt

import models
import schemas
from database import engine, get_db, get_redis

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="iTechSmart Ledger API",
    description="Blockchain Integration Platform - Manage wallets, transactions, and smart contracts",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Helper Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# Root Endpoint
@app.get("/")
async def root():
    return {
        "message": "iTechSmart Ledger API",
        "version": "1.0.0",
        "status": "operational"
    }

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Authentication Endpoints
@app.post("/auth/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.UserResponse)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    return current_user

# Wallet Endpoints
@app.post("/wallets", response_model=schemas.WalletResponse)
async def create_wallet(
    wallet: schemas.WalletCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Generate wallet address (simplified - in production use proper blockchain libraries)
    wallet_address = f"0x{secrets.token_hex(20)}"
    
    db_wallet = models.Wallet(
        user_id=current_user.id,
        name=wallet.name,
        address=wallet_address,
        network=wallet.network,
        wallet_type=wallet.wallet_type
    )
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

@app.get("/wallets", response_model=List[schemas.WalletResponse])
async def get_wallets(
    skip: int = 0,
    limit: int = 100,
    network: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id)
    if network:
        query = query.filter(models.Wallet.network == network)
    wallets = query.offset(skip).limit(limit).all()
    return wallets

@app.get("/wallets/{wallet_id}", response_model=schemas.WalletResponse)
async def get_wallet(
    wallet_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wallet = db.query(models.Wallet).filter(
        models.Wallet.id == wallet_id,
        models.Wallet.user_id == current_user.id
    ).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet

@app.delete("/wallets/{wallet_id}")
async def delete_wallet(
    wallet_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wallet = db.query(models.Wallet).filter(
        models.Wallet.id == wallet_id,
        models.Wallet.user_id == current_user.id
    ).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    db.delete(wallet)
    db.commit()
    return {"message": "Wallet deleted successfully"}

# Transaction Endpoints
@app.post("/transactions", response_model=schemas.TransactionResponse)
async def create_transaction(
    transaction: schemas.TransactionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify wallet ownership
    wallet = db.query(models.Wallet).filter(
        models.Wallet.id == transaction.from_wallet_id,
        models.Wallet.user_id == current_user.id
    ).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # Generate transaction hash (simplified)
    tx_hash = f"0x{secrets.token_hex(32)}"
    
    db_transaction = models.Transaction(
        user_id=current_user.id,
        from_wallet_id=transaction.from_wallet_id,
        from_address=wallet.address,
        to_address=transaction.to_address,
        network=transaction.network,
        amount=transaction.amount,
        transaction_hash=tx_hash,
        status=models.TransactionStatus.PENDING,
        metadata=transaction.metadata
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions", response_model=List[schemas.TransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    network: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id)
    if status:
        query = query.filter(models.Transaction.status == status)
    if network:
        query = query.filter(models.Transaction.network == network)
    transactions = query.order_by(models.Transaction.created_at.desc()).offset(skip).limit(limit).all()
    return transactions

@app.get("/transactions/{transaction_id}", response_model=schemas.TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

# Smart Contract Endpoints
@app.post("/contracts", response_model=schemas.SmartContractResponse)
async def create_contract(
    contract: schemas.SmartContractCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_contract = models.SmartContract(
        user_id=current_user.id,
        name=contract.name,
        description=contract.description,
        network=contract.network,
        source_code=contract.source_code,
        compiler_version=contract.compiler_version,
        status=models.ContractStatus.DRAFT
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

@app.get("/contracts", response_model=List[schemas.SmartContractResponse])
async def get_contracts(
    skip: int = 0,
    limit: int = 100,
    network: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.SmartContract).filter(models.SmartContract.user_id == current_user.id)
    if network:
        query = query.filter(models.SmartContract.network == network)
    contracts = query.offset(skip).limit(limit).all()
    return contracts

@app.get("/contracts/{contract_id}", response_model=schemas.SmartContractResponse)
async def get_contract(
    contract_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(models.SmartContract).filter(
        models.SmartContract.id == contract_id,
        models.SmartContract.user_id == current_user.id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@app.post("/contracts/{contract_id}/deploy")
async def deploy_contract(
    contract_id: int,
    deploy_data: schemas.SmartContractDeploy,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(models.SmartContract).filter(
        models.SmartContract.id == contract_id,
        models.SmartContract.user_id == current_user.id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Generate contract address (simplified)
    contract_address = f"0x{secrets.token_hex(20)}"
    deployment_tx = f"0x{secrets.token_hex(32)}"
    
    contract.contract_address = contract_address
    contract.deployment_transaction = deployment_tx
    contract.status = models.ContractStatus.DEPLOYED
    contract.deployed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(contract)
    return {"message": "Contract deployed successfully", "address": contract_address, "transaction": deployment_tx}

# Contract Interaction Endpoints
@app.post("/contracts/interact", response_model=schemas.ContractInteractionResponse)
async def interact_with_contract(
    interaction: schemas.ContractInteractionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(models.SmartContract).filter(
        models.SmartContract.id == interaction.contract_id,
        models.SmartContract.user_id == current_user.id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    tx_hash = f"0x{secrets.token_hex(32)}"
    
    db_interaction = models.ContractInteraction(
        contract_id=interaction.contract_id,
        user_id=current_user.id,
        function_name=interaction.function_name,
        parameters=interaction.parameters,
        transaction_hash=tx_hash,
        status=models.TransactionStatus.PENDING
    )
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

@app.get("/contracts/{contract_id}/interactions", response_model=List[schemas.ContractInteractionResponse])
async def get_contract_interactions(
    contract_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interactions = db.query(models.ContractInteraction).filter(
        models.ContractInteraction.contract_id == contract_id,
        models.ContractInteraction.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return interactions

# Block Explorer Endpoints
@app.get("/blocks", response_model=List[schemas.BlockResponse])
async def get_blocks(
    network: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    blocks = db.query(models.Block).filter(
        models.Block.network == network
    ).order_by(models.Block.block_number.desc()).offset(skip).limit(limit).all()
    return blocks

@app.get("/blocks/{block_number}", response_model=schemas.BlockResponse)
async def get_block(
    network: str,
    block_number: int,
    db: Session = Depends(get_db)
):
    block = db.query(models.Block).filter(
        models.Block.network == network,
        models.Block.block_number == block_number
    ).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block

# Token Endpoints
@app.post("/tokens", response_model=schemas.TokenResponse)
async def create_token(
    token: schemas.TokenCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_token = models.Token(
        network=token.network,
        contract_address=token.contract_address,
        name=token.name,
        symbol=token.symbol,
        decimals=token.decimals,
        token_type=token.token_type,
        logo_url=token.logo_url
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

@app.get("/tokens", response_model=List[schemas.TokenResponse])
async def get_tokens(
    network: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.Token)
    if network:
        query = query.filter(models.Token.network == network)
    tokens = query.offset(skip).limit(limit).all()
    return tokens

@app.get("/wallets/{wallet_id}/tokens", response_model=List[schemas.TokenBalanceResponse])
async def get_wallet_token_balances(
    wallet_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wallet = db.query(models.Wallet).filter(
        models.Wallet.id == wallet_id,
        models.Wallet.user_id == current_user.id
    ).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    balances = db.query(models.TokenBalance).filter(
        models.TokenBalance.wallet_id == wallet_id
    ).all()
    return balances

# Network Configuration Endpoints
@app.post("/networks", response_model=schemas.NetworkConfigResponse)
async def create_network_config(
    config: schemas.NetworkConfigCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db_config = models.NetworkConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@app.get("/networks", response_model=List[schemas.NetworkConfigResponse])
async def get_network_configs(
    db: Session = Depends(get_db)
):
    configs = db.query(models.NetworkConfig).filter(models.NetworkConfig.is_active == True).all()
    return configs

# Analytics Endpoints
@app.get("/analytics/dashboard", response_model=schemas.DashboardStats)
async def get_dashboard_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_wallets = db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).count()
    total_transactions = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id).count()
    total_contracts = db.query(models.SmartContract).filter(models.SmartContract.user_id == current_user.id).count()
    
    # Calculate total volume
    total_volume = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.status == models.TransactionStatus.CONFIRMED
    ).with_entities(models.Transaction.amount).all()
    total_volume = sum([t[0] for t in total_volume]) if total_volume else 0.0
    
    # Network stats
    network_stats = []
    for network in models.BlockchainNetwork:
        network_txs = db.query(models.Transaction).filter(
            models.Transaction.user_id == current_user.id,
            models.Transaction.network == network
        ).count()
        
        network_wallets = db.query(models.Wallet).filter(
            models.Wallet.user_id == current_user.id,
            models.Wallet.network == network
        ).count()
        
        network_volume = db.query(models.Transaction).filter(
            models.Transaction.user_id == current_user.id,
            models.Transaction.network == network,
            models.Transaction.status == models.TransactionStatus.CONFIRMED
        ).with_entities(models.Transaction.amount).all()
        network_volume = sum([t[0] for t in network_volume]) if network_volume else 0.0
        
        avg_fee = db.query(models.Transaction).filter(
            models.Transaction.user_id == current_user.id,
            models.Transaction.network == network,
            models.Transaction.status == models.TransactionStatus.CONFIRMED
        ).with_entities(models.Transaction.fee).all()
        avg_fee = sum([t[0] for t in avg_fee]) / len(avg_fee) if avg_fee else 0.0
        
        network_stats.append(schemas.NetworkStats(
            network=network,
            total_transactions=network_txs,
            total_wallets=network_wallets,
            total_volume=network_volume,
            avg_transaction_fee=avg_fee
        ))
    
    return schemas.DashboardStats(
        total_wallets=total_wallets,
        total_transactions=total_transactions,
        total_smart_contracts=total_contracts,
        total_volume=total_volume,
        network_stats=network_stats
    )

# API Key Endpoints
@app.post("/api-keys", response_model=schemas.APIKeyResponse)
async def create_api_key(
    api_key: schemas.APIKeyCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    key = f"lk_{secrets.token_urlsafe(32)}"
    
    db_api_key = models.APIKey(
        user_id=current_user.id,
        name=api_key.name,
        key=key,
        rate_limit=api_key.rate_limit,
        allowed_networks=api_key.allowed_networks,
        expires_at=api_key.expires_at
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

@app.get("/api-keys", response_model=List[schemas.APIKeyResponse])
async def get_api_keys(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_keys = db.query(models.APIKey).filter(models.APIKey.user_id == current_user.id).all()
    return api_keys

@app.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_key = db.query(models.APIKey).filter(
        models.APIKey.id == key_id,
        models.APIKey.user_id == current_user.id
    ).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    db.delete(api_key)
    db.commit()
    return {"message": "API key deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)