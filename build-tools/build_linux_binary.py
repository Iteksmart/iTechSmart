"""
Linux Binary Builder
Builds production-ready Linux binaries for iTechSmart products
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path


class LinuxBuilder:
    """Build Linux binaries using PyInstaller"""

    def __init__(self, product_name: str, version: str):
        self.product_name = product_name
        self.version = version
        self.workspace = Path.cwd()
        self.product_dir = self.workspace / product_name
        self.build_dir = self.workspace / "build" / "linux" / product_name
        self.dist_dir = self.workspace / "dist" / "linux" / product_name

    def prepare_environment(self):
        """Prepare build environment"""
        print(f"Preparing build environment for {self.product_name}...")

        # Create directories
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.dist_dir.mkdir(parents=True, exist_ok=True)

        # Copy license system
        license_src = self.workspace / "src" / "license-system"
        license_dst = self.product_dir / "backend" / "license_system"
        if license_src.exists():
            shutil.copytree(license_src, license_dst, dirs_exist_ok=True)
            print(f"✓ License system copied")

        # Copy auto-update system
        update_src = self.workspace / "src" / "auto-update"
        update_dst = self.product_dir / "backend" / "auto_update"
        if update_src.exists():
            shutil.copytree(update_src, update_dst, dirs_exist_ok=True)
            print(f"✓ Auto-update system copied")

    def find_entry_point(self) -> Path:
        """Find the main entry point for the application"""
        possible_entries = [
            self.product_dir / "backend" / "main.py",
            self.product_dir / "backend" / "app" / "main.py",
            self.product_dir / "backend" / "app.py",
            self.product_dir / "main.py",
        ]

        for entry in possible_entries:
            if entry.exists():
                print(f"✓ Found entry point: {entry}")
                return entry

        raise FileNotFoundError(f"No entry point found for {self.product_name}")

    def build_frontend(self):
        """Build frontend if it exists"""
        frontend_dir = self.product_dir / "frontend"
        if not frontend_dir.exists():
            print("No frontend found, skipping...")
            return

        print("Building frontend...")

        if not (frontend_dir / "package.json").exists():
            print("No package.json found, skipping frontend build")
            return

        try:
            subprocess.run(
                ["npm", "install"], cwd=frontend_dir, check=True, capture_output=True
            )
            subprocess.run(
                ["npm", "run", "build"],
                cwd=frontend_dir,
                check=True,
                capture_output=True,
            )
            print("✓ Frontend built successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠ Frontend build failed: {e}")

    def create_spec_file(self, entry_point: Path):
        """Create PyInstaller spec file for Linux"""
        print("Creating PyInstaller spec file...")

        metadata = self.get_product_metadata()
        data_files = self.collect_data_files()
        hidden_imports = self.get_hidden_imports()

        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{entry_point}'],
    pathex=['{self.product_dir / "backend"}'],
    binaries=[],
    datas={data_files},
    hiddenimports={hidden_imports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'numpy.distutils'],
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
    name='{self.product_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

        spec_file = self.build_dir / f"{self.product_name}.spec"
        spec_file.write_text(spec_content)
        print(f"✓ Spec file created: {spec_file}")
        return spec_file

    def collect_data_files(self) -> list:
        """Collect data files to include in the build"""
        data_files = []

        frontend_dist = self.product_dir / "frontend" / "dist"
        if frontend_dist.exists():
            data_files.append((str(frontend_dist), "frontend/dist"))

        static_dir = self.product_dir / "backend" / "static"
        if static_dir.exists():
            data_files.append((str(static_dir), "static"))

        templates_dir = self.product_dir / "backend" / "templates"
        if templates_dir.exists():
            data_files.append((str(templates_dir), "templates"))

        config_dir = self.product_dir / "backend" / "config"
        if config_dir.exists():
            data_files.append((str(config_dir), "config"))

        return data_files

    def get_hidden_imports(self) -> list:
        """Get list of hidden imports"""
        return [
            "uvicorn.logging",
            "uvicorn.loops",
            "uvicorn.loops.auto",
            "uvicorn.protocols",
            "uvicorn.protocols.http",
            "uvicorn.protocols.http.auto",
            "uvicorn.protocols.websockets",
            "uvicorn.protocols.websockets.auto",
            "uvicorn.lifespan",
            "uvicorn.lifespan.on",
            "fastapi",
            "pydantic",
            "sqlalchemy",
            "cryptography",
            "license_system",
            "auto_update",
        ]

    def get_product_metadata(self) -> dict:
        """Get product metadata"""
        metadata_file = self.product_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                return json.load(f)

        return {
            "name": self.product_name.replace("-", " ").title(),
            "description": f"{self.product_name} - iTechSmart Suite",
            "version": self.version,
            "company": "iTechSmart",
            "copyright": "Copyright © 2025 iTechSmart. All rights reserved.",
        }

    def build_binary(self, spec_file: Path):
        """Build the binary using PyInstaller"""
        print(f"Building {self.product_name} binary...")

        try:
            import PyInstaller.__main__

            PyInstaller.__main__.run(
                [
                    str(spec_file),
                    "--distpath",
                    str(self.dist_dir),
                    "--workpath",
                    str(self.build_dir / "work"),
                    "--clean",
                    "--noconfirm",
                ]
            )

            # Make executable
            binary_path = self.dist_dir / self.product_name
            if binary_path.exists():
                os.chmod(binary_path, 0o755)

            print(f"✓ Binary built successfully")
            print(f"  Output: {binary_path}")

        except Exception as e:
            print(f"✗ Build failed: {e}")
            raise

    def create_desktop_file(self):
        """Create .desktop file for Linux"""
        metadata = self.get_product_metadata()

        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={metadata['name']}
Comment={metadata['description']}
Exec={self.product_name}
Icon={self.product_name}
Terminal=false
Categories=Utility;Development;
"""

        desktop_file = self.dist_dir / f"{self.product_name}.desktop"
        desktop_file.write_text(desktop_content)
        os.chmod(desktop_file, 0o755)

        print(f"✓ Desktop file created: {desktop_file}")

    def create_version_file(self):
        """Create version information file"""
        version_info = {
            "product": self.product_name,
            "version": self.version,
            "build_date": subprocess.check_output(
                ["git", "log", "-1", "--format=%cd", "--date=iso"], text=True
            ).strip(),
            "commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip()[:8],
        }

        version_file = self.dist_dir / "version.json"
        with open(version_file, "w") as f:
            json.dump(version_info, f, indent=2)

        print(f"✓ Version file created: {version_file}")

    def run(self):
        """Run the complete build process"""
        print("=" * 60)
        print(f"Building Linux Binary: {self.product_name}")
        print(f"Version: {self.version}")
        print("=" * 60)

        try:
            self.prepare_environment()
            self.build_frontend()
            entry_point = self.find_entry_point()
            spec_file = self.create_spec_file(entry_point)
            self.build_binary(spec_file)
            self.create_desktop_file()
            self.create_version_file()

            print("\n" + "=" * 60)
            print("✓ BUILD SUCCESSFUL")
            print("=" * 60)
            print(f"Output directory: {self.dist_dir}")

            return True

        except Exception as e:
            print("\n" + "=" * 60)
            print("✗ BUILD FAILED")
            print("=" * 60)
            print(f"Error: {e}")
            return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python build_linux_binary.py <product_name> <version>")
        sys.exit(1)

    product_name = sys.argv[1]
    version = sys.argv[2]

    builder = LinuxBuilder(product_name, version)
    success = builder.run()

    sys.exit(0 if success else 1)
