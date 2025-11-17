"""
Deployments API Routes
Handles deployment of websites and applications to various platforms
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pathlib import Path
import shutil
import subprocess
import json
import logging
from datetime import datetime

from app.core.database import get_db
from app.models.database import User
from app.api.auth import get_current_user
from pydantic import BaseModel, HttpUrl

logger = logging.getLogger(__name__)

router = APIRouter()

# Deployment directory
DEPLOY_DIR = Path("deployments")
DEPLOY_DIR.mkdir(exist_ok=True)


class DeploymentCreate(BaseModel):
    name: str
    platform: str  # vercel, netlify, github-pages, s3
    source_path: str
    config: Dict = {}


class DeploymentResponse(BaseModel):
    id: str
    name: str
    platform: str
    status: str
    url: Optional[str]
    created_at: str
    deployed_at: Optional[str]
    error: Optional[str]


class DeploymentConfig(BaseModel):
    vercel_token: Optional[str] = None
    netlify_token: Optional[str] = None
    github_token: Optional[str] = None
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    aws_region: Optional[str] = "us-east-1"


# In-memory deployment storage (in production, use database)
deployments_db: Dict[str, dict] = {}


def get_user_deploy_dir(user_id: int) -> Path:
    """Get deployment directory for specific user"""
    user_dir = DEPLOY_DIR / str(user_id)
    user_dir.mkdir(exist_ok=True)
    return user_dir


def generate_deployment_id() -> str:
    """Generate unique deployment ID"""
    import uuid

    return f"deploy_{uuid.uuid4().hex[:12]}"


async def deploy_to_vercel(
    deployment_id: str, name: str, source_path: Path, config: dict
) -> dict:
    """Deploy to Vercel"""
    try:
        vercel_token = config.get("vercel_token")
        if not vercel_token:
            raise ValueError("Vercel token not provided")

        # Create vercel.json if not exists
        vercel_config = source_path / "vercel.json"
        if not vercel_config.exists():
            with open(vercel_config, "w") as f:
                json.dump(
                    {
                        "version": 2,
                        "name": name,
                        "builds": [{"src": "**/*.html", "use": "@vercel/static"}],
                    },
                    f,
                )

        # Deploy using Vercel CLI
        cmd = ["vercel", "--token", vercel_token, "--prod", "--yes", str(source_path)]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise Exception(f"Vercel deployment failed: {result.stderr}")

        # Extract URL from output
        url = result.stdout.strip().split("\n")[-1]

        return {
            "status": "deployed",
            "url": url,
            "deployed_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Vercel deployment error: {e}")
        return {"status": "failed", "error": str(e)}


async def deploy_to_netlify(
    deployment_id: str, name: str, source_path: Path, config: dict
) -> dict:
    """Deploy to Netlify"""
    try:
        netlify_token = config.get("netlify_token")
        if not netlify_token:
            raise ValueError("Netlify token not provided")

        # Deploy using Netlify CLI
        cmd = [
            "netlify",
            "deploy",
            "--prod",
            "--auth",
            netlify_token,
            "--dir",
            str(source_path),
            "--site",
            name,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise Exception(f"Netlify deployment failed: {result.stderr}")

        # Extract URL from output
        lines = result.stdout.strip().split("\n")
        url = None
        for line in lines:
            if "Website URL:" in line:
                url = line.split("Website URL:")[-1].strip()
                break

        return {
            "status": "deployed",
            "url": url or f"https://{name}.netlify.app",
            "deployed_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Netlify deployment error: {e}")
        return {"status": "failed", "error": str(e)}


async def deploy_to_github_pages(
    deployment_id: str, name: str, source_path: Path, config: dict
) -> dict:
    """Deploy to GitHub Pages"""
    try:
        github_token = config.get("github_token")
        repo = config.get("github_repo")

        if not github_token or not repo:
            raise ValueError("GitHub token and repo required")

        # Initialize git repo if not exists
        git_dir = source_path / ".git"
        if not git_dir.exists():
            subprocess.run(["git", "init"], cwd=source_path, check=True)
            subprocess.run(
                [
                    "git",
                    "remote",
                    "add",
                    "origin",
                    f"https://{github_token}@github.com/{repo}.git",
                ],
                cwd=source_path,
                check=True,
            )

        # Commit and push
        subprocess.run(["git", "add", "."], cwd=source_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Deploy {deployment_id}"],
            cwd=source_path,
            check=True,
        )
        subprocess.run(
            ["git", "push", "-f", "origin", "main:gh-pages"],
            cwd=source_path,
            check=True,
        )

        # Extract username and repo name
        username = repo.split("/")[0]
        repo_name = repo.split("/")[1]

        return {
            "status": "deployed",
            "url": f"https://{username}.github.io/{repo_name}",
            "deployed_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"GitHub Pages deployment error: {e}")
        return {"status": "failed", "error": str(e)}


async def deploy_to_s3(
    deployment_id: str, name: str, source_path: Path, config: dict
) -> dict:
    """Deploy to AWS S3"""
    try:
        import boto3

        aws_access_key = config.get("aws_access_key")
        aws_secret_key = config.get("aws_secret_key")
        aws_region = config.get("aws_region", "us-east-1")
        bucket_name = config.get("bucket_name", name)

        if not aws_access_key or not aws_secret_key:
            raise ValueError("AWS credentials required")

        # Create S3 client
        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )

        # Create bucket if not exists
        try:
            s3.create_bucket(Bucket=bucket_name)

            # Enable static website hosting
            s3.put_bucket_website(
                Bucket=bucket_name,
                WebsiteConfiguration={
                    "IndexDocument": {"Suffix": "index.html"},
                    "ErrorDocument": {"Key": "error.html"},
                },
            )

            # Make bucket public
            s3.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "PublicReadGetObject",
                                "Effect": "Allow",
                                "Principal": "*",
                                "Action": "s3:GetObject",
                                "Resource": f"arn:aws:s3:::{bucket_name}/*",
                            }
                        ],
                    }
                ),
            )
        except Exception as e:
            logger.warning(f"Bucket creation warning: {e}")

        # Upload files
        for file_path in source_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(source_path)
                s3.upload_file(
                    str(file_path),
                    bucket_name,
                    str(relative_path),
                    ExtraArgs={
                        "ContentType": (
                            "text/html"
                            if file_path.suffix == ".html"
                            else "application/octet-stream"
                        )
                    },
                )

        url = f"http://{bucket_name}.s3-website-{aws_region}.amazonaws.com"

        return {
            "status": "deployed",
            "url": url,
            "deployed_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"S3 deployment error: {e}")
        return {"status": "failed", "error": str(e)}


@router.post(
    "/", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED
)
async def create_deployment(
    deployment_data: DeploymentCreate, current_user: User = Depends(get_current_user)
):
    """
    Create a new deployment

    - **name**: Deployment name
    - **platform**: Target platform (vercel, netlify, github-pages, s3)
    - **source_path**: Path to source files (relative to user's upload directory)
    - **config**: Platform-specific configuration
    """
    # Validate platform
    valid_platforms = ["vercel", "netlify", "github-pages", "s3"]
    if deployment_data.platform not in valid_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}",
        )

    # Get source path
    source_path = Path("uploads") / str(current_user.id) / deployment_data.source_path
    if not source_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source path not found"
        )

    # Generate deployment ID
    deployment_id = generate_deployment_id()

    # Create deployment record
    deployment = {
        "id": deployment_id,
        "user_id": current_user.id,
        "name": deployment_data.name,
        "platform": deployment_data.platform,
        "source_path": str(source_path),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "deployed_at": None,
        "url": None,
        "error": None,
    }

    deployments_db[deployment_id] = deployment

    logger.info(f"Deployment created: {deployment_id} by user {current_user.email}")

    # Deploy based on platform
    try:
        if deployment_data.platform == "vercel":
            result = await deploy_to_vercel(
                deployment_id, deployment_data.name, source_path, deployment_data.config
            )
        elif deployment_data.platform == "netlify":
            result = await deploy_to_netlify(
                deployment_id, deployment_data.name, source_path, deployment_data.config
            )
        elif deployment_data.platform == "github-pages":
            result = await deploy_to_github_pages(
                deployment_id, deployment_data.name, source_path, deployment_data.config
            )
        elif deployment_data.platform == "s3":
            result = await deploy_to_s3(
                deployment_id, deployment_data.name, source_path, deployment_data.config
            )

        # Update deployment record
        deployment.update(result)

    except Exception as e:
        logger.error(f"Deployment error: {e}")
        deployment["status"] = "failed"
        deployment["error"] = str(e)

    return DeploymentResponse(**deployment)


@router.get("/", response_model=List[DeploymentResponse])
async def list_deployments(current_user: User = Depends(get_current_user)):
    """List all deployments for current user"""
    user_deployments = [
        DeploymentResponse(**d)
        for d in deployments_db.values()
        if d["user_id"] == current_user.id
    ]

    # Sort by created_at (newest first)
    user_deployments.sort(key=lambda x: x.created_at, reverse=True)

    return user_deployments


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: str, current_user: User = Depends(get_current_user)
):
    """Get deployment details"""
    deployment = deployments_db.get(deployment_id)

    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found"
        )

    if deployment["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this deployment",
        )

    return DeploymentResponse(**deployment)


@router.delete("/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deployment(
    deployment_id: str, current_user: User = Depends(get_current_user)
):
    """Delete a deployment record"""
    deployment = deployments_db.get(deployment_id)

    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found"
        )

    if deployment["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this deployment",
        )

    del deployments_db[deployment_id]

    logger.info(f"Deployment deleted: {deployment_id}")

    return None
