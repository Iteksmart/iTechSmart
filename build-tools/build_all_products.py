"""
iTechSmart Suite - Build All Products
Creates encrypted executables for all 36 products
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# List of all 36 products
PRODUCTS = [
    {"name": "iTechSmart Enterprise", "dir": "itechsmart-enterprise", "port": 8001, "frontend_port": 3001},
    {"name": "iTechSmart Ninja", "dir": "itechsmart-ninja", "port": 8002, "frontend_port": 3002},
    {"name": "iTechSmart Analytics", "dir": "itechsmart-analytics", "port": 8003, "frontend_port": 3003},
    {"name": "iTechSmart Supreme", "dir": "itechsmart-supreme", "port": 8004, "frontend_port": 3004},
    {"name": "iTechSmart HL7", "dir": "itechsmart-hl7", "port": 8005, "frontend_port": 3005},
    {"name": "ProofLink", "dir": "prooflink", "port": 8006, "frontend_port": 3006},
    {"name": "PassPort", "dir": "passport", "port": 8007, "frontend_port": 3007},
    {"name": "ImpactOS", "dir": "itechsmart-impactos", "port": 8008, "frontend_port": 3008},
    {"name": "LegalAI Pro", "dir": "legalai-pro", "port": 8009, "frontend_port": 3009},
    {"name": "iTechSmart DataFlow", "dir": "itechsmart-dataflow", "port": 8010, "frontend_port": 3010},
    {"name": "iTechSmart Pulse", "dir": "itechsmart-pulse", "port": 8011, "frontend_port": 3011},
    {"name": "iTechSmart Connect", "dir": "itechsmart-connect", "port": 8012, "frontend_port": 3012},
    {"name": "iTechSmart Vault", "dir": "itechsmart-vault", "port": 8013, "frontend_port": 3013},
    {"name": "iTechSmart Notify", "dir": "itechsmart-notify", "port": 8014, "frontend_port": 3014},
    {"name": "iTechSmart Ledger", "dir": "itechsmart-ledger", "port": 8015, "frontend_port": 3015},
    {"name": "iTechSmart Copilot", "dir": "itechsmart-copilot", "port": 8016, "frontend_port": 3016},
    {"name": "iTechSmart Shield", "dir": "itechsmart-shield", "port": 8017, "frontend_port": 3017},
    {"name": "iTechSmart Workflow", "dir": "itechsmart-workflow", "port": 8018, "frontend_port": 3018},
    {"name": "iTechSmart Marketplace", "dir": "itechsmart-marketplace", "port": 8019, "frontend_port": 3019},
    {"name": "iTechSmart Cloud", "dir": "itechsmart-cloud", "port": 8020, "frontend_port": 3020},
    {"name": "iTechSmart DevOps", "dir": "itechsmart-devops", "port": 8021, "frontend_port": 3021},
    {"name": "iTechSmart Mobile", "dir": "itechsmart-mobile", "port": 8022, "frontend_port": 3022},
    {"name": "iTechSmart AI", "dir": "itechsmart-ai", "port": 8023, "frontend_port": 3023},
    {"name": "iTechSmart Compliance", "dir": "itechsmart-compliance", "port": 8024, "frontend_port": 3024},
    {"name": "iTechSmart Data Platform", "dir": "itechsmart-data-platform", "port": 8025, "frontend_port": 3025},
    {"name": "iTechSmart Customer Success", "dir": "itechsmart-customer-success", "port": 8026, "frontend_port": 3026},
    {"name": "iTechSmart Port Manager", "dir": "itechsmart-port-manager", "port": 8100, "frontend_port": 3100},
    {"name": "iTechSmart MDM Agent", "dir": "itechsmart-mdm-agent", "port": 8200, "frontend_port": 3200},
    {"name": "iTechSmart QA/QC", "dir": "itechsmart-qaqc", "port": 8300, "frontend_port": 3300},
    {"name": "iTechSmart Think-Tank", "dir": "itechsmart-think-tank", "port": 8030, "frontend_port": 3030},
    {"name": "iTechSmart Sentinel", "dir": "itechsmart-sentinel", "port": 8031, "frontend_port": 3031},
    {"name": "iTechSmart Forge", "dir": "itechsmart-forge", "port": 8032, "frontend_port": 3032},
    {"name": "iTechSmart Sandbox", "dir": "itechsmart-sandbox", "port": 8033, "frontend_port": 3033},
    {"name": "iTechSmart Supreme Plus", "dir": "itechsmart-supreme-plus", "port": 8034, "frontend_port": 3034},
    {"name": "iTechSmart Citadel", "dir": "itechsmart-citadel", "port": 8035, "frontend_port": 3035},
    {"name": "iTechSmart Observatory", "dir": "itechsmart-observatory", "port": 8036, "frontend_port": 3036},
]

class ProductBuilder:
    """Builds encrypted executables for products"""
    
    def __init__(self, output_dir: str = "installers"):
        self.output_dir = output_dir
        self.workspace = os.getcwd()
        
    def build_product(self, product: dict, platform_type: str = "windows") -> bool:
        """Build a single product"""
        print(f"\n{'='*60}")
        print(f"Building: {product['name']}")
        print(f"{'='*60}")
        
        product_dir = os.path.join(self.workspace, product['dir'])
        
        # Check if product directory exists
        if not os.path.exists(product_dir):
            print(f"⚠️  Product directory not found: {product_dir}")
            return False
        
        # Find main entry point
        main_file = self._find_main_file(product_dir)
        if not main_file:
            print(f"⚠️  Main file not found for {product['name']}")
            return False
        
        print(f"✓ Found main file: {main_file}")
        
        # Create PyInstaller spec
        spec_file = self._create_spec_file(product, main_file, platform_type)
        print(f"✓ Created spec file: {spec_file}")
        
        # Encrypt with PyArmor
        encrypted_dir = self._encrypt_with_pyarmor(product_dir)
        if encrypted_dir:
            print(f"✓ Code encrypted with PyArmor")
        
        # Build with PyInstaller
        success = self._build_with_pyinstaller(spec_file, platform_type)
        
        if success:
            print(f"✅ Successfully built {product['name']}")
        else:
            print(f"❌ Failed to build {product['name']}")
        
        return success
    
    def _find_main_file(self, product_dir: str) -> str:
        """Find main entry point file"""
        # Common main file names
        candidates = [
            "main.py",
            "app.py",
            "server.py",
            "run.py",
            "__main__.py",
            "backend/main.py",
            "backend/app.py",
            "backend/server.py"
        ]
        
        for candidate in candidates:
            filepath = os.path.join(product_dir, candidate)
            if os.path.exists(filepath):
                return filepath
        
        return None
    
    def _create_spec_file(self, product: dict, main_file: str, platform_type: str) -> str:
        """Create PyInstaller spec file"""
        product_name = product['name'].replace(" ", "-").lower()
        spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{main_file}'],
    pathex=[],
    binaries=[],
    datas=[
        ('installers/assets/logo-256.png', 'assets'),
        ('installers/assets/splash/splash-screen.png', 'assets'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'cryptography',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{product_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='installers/assets/icons/itechsmart.ico',
)
"""
        
        spec_file = f"build-tools/{product_name}.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        return spec_file
    
    def _encrypt_with_pyarmor(self, product_dir: str) -> str:
        """Encrypt code with PyArmor"""
        try:
            encrypted_dir = f"{product_dir}_encrypted"
            
            # Remove old encrypted directory
            if os.path.exists(encrypted_dir):
                shutil.rmtree(encrypted_dir)
            
            # Encrypt with PyArmor
            subprocess.run([
                "pyarmor",
                "gen",
                "-O", encrypted_dir,
                "-r",
                product_dir
            ], check=True, capture_output=True)
            
            return encrypted_dir
            
        except Exception as e:
            print(f"⚠️  PyArmor encryption failed: {str(e)}")
            return None
    
    def _build_with_pyinstaller(self, spec_file: str, platform_type: str) -> bool:
        """Build with PyInstaller"""
        try:
            subprocess.run([
                "pyinstaller",
                "--clean",
                "--noconfirm",
                spec_file
            ], check=True)
            
            return True
            
        except Exception as e:
            print(f"❌ PyInstaller build failed: {str(e)}")
            return False
    
    def build_all(self, platform_type: str = "windows"):
        """Build all products"""
        print(f"\n{'='*60}")
        print(f"Building All 36 Products for {platform_type}")
        print(f"{'='*60}\n")
        
        success_count = 0
        failed_products = []
        
        for i, product in enumerate(PRODUCTS, 1):
            print(f"\n[{i}/36] Building {product['name']}...")
            
            if self.build_product(product, platform_type):
                success_count += 1
            else:
                failed_products.append(product['name'])
        
        # Summary
        print(f"\n{'='*60}")
        print(f"Build Summary")
        print(f"{'='*60}")
        print(f"✅ Successful: {success_count}/36")
        print(f"❌ Failed: {len(failed_products)}/36")
        
        if failed_products:
            print(f"\nFailed products:")
            for product in failed_products:
                print(f"  - {product}")
        
        return success_count == 36


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build iTechSmart Suite products")
    parser.add_argument(
        "--platform",
        choices=["windows", "linux", "macos", "all"],
        default="windows",
        help="Target platform"
    )
    parser.add_argument(
        "--product",
        help="Build specific product (by name)"
    )
    
    args = parser.parse_args()
    
    builder = ProductBuilder()
    
    if args.product:
        # Build specific product
        product = next((p for p in PRODUCTS if p['name'] == args.product), None)
        if product:
            builder.build_product(product, args.platform)
        else:
            print(f"Product not found: {args.product}")
            sys.exit(1)
    else:
        # Build all products
        if args.platform == "all":
            for platform in ["windows", "linux", "macos"]:
                builder.build_all(platform)
        else:
            builder.build_all(args.platform)