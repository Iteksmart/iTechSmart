# iTechSmart Suite - Client Customization Guide

**Version**: 1.0.0  
**Date**: January 13, 2025  
**Purpose**: Guide for creating custom-branded installers for clients

---

## 🎯 Overview

This guide explains how to create fully customized installers for your clients with their own branding, company information, and configuration. The build system supports complete white-labeling and customization.

---

## 📋 What Can Be Customized

### ✅ Branding & Visual Identity
- Client logo (all sizes)
- Splash screens
- Icons (.ico, .icns, .png)
- Color schemes
- Company name throughout

### ✅ Company Information
- Company name
- Website URL
- Support email
- Contact information
- Copyright notices
- Legal information

### ✅ Product Configuration
- Product selection (which of the 36 products to include)
- Feature enablement
- Default settings
- License restrictions
- Trial period duration

### ✅ Installation Options
- Installation directory
- Service names
- Port configurations
- Database settings
- Network settings

### ✅ License Configuration
- License types available
- Feature restrictions per type
- Trial period settings
- Activation requirements
- License server URL

### ✅ Update Configuration
- Update server URL
- Update frequency
- Auto-update settings
- Version checking

### ✅ Telemetry Configuration
- Telemetry server URL
- Data collection settings
- Privacy settings
- Analytics configuration

---

## 🛠️ Customization Process

### Step 1: Create Client Configuration File

Create a JSON configuration file for each client:

```json
{
  "client": {
    "name": "Acme Corporation",
    "short_name": "Acme",
    "website": "https://www.acme.com",
    "support_email": "support@acme.com",
    "support_phone": "+1-555-0123",
    "copyright": "Copyright © 2025 Acme Corporation. All rights reserved."
  },
  "branding": {
    "logo_file": "clients/acme/logo.png",
    "primary_color": "#0066CC",
    "secondary_color": "#FF6600",
    "app_name": "Acme Enterprise Suite",
    "installer_name": "Acme-Enterprise-Suite-Setup"
  },
  "products": {
    "include": [1, 2, 3, 4, 5, 10, 11, 12, 17, 24],
    "exclude": [],
    "custom_names": {
      "iTechSmart Enterprise": "Acme Integration Hub",
      "iTechSmart Shield": "Acme Security Platform"
    }
  },
  "license": {
    "types": ["trial", "basic", "professional", "enterprise"],
    "trial_days": 30,
    "default_type": "trial",
    "require_activation": true,
    "license_server": "https://license.acme.com/api/v1"
  },
  "update": {
    "update_server": "https://updates.acme.com/api/v1",
    "check_frequency": 86400,
    "auto_update": false,
    "allow_manual_check": true
  },
  "telemetry": {
    "enabled": true,
    "server": "https://telemetry.acme.com/api/v1",
    "anonymous": true,
    "collect_system_info": true,
    "collect_usage_stats": true
  },
  "installation": {
    "default_dir": "C:\\Program Files\\Acme Enterprise Suite",
    "create_desktop_shortcut": true,
    "create_start_menu": true,
    "auto_start": false,
    "ports": {
      "base_port": 9000,
      "frontend_base_port": 4000
    }
  },
  "features": {
    "enable_crash_reporting": true,
    "enable_analytics": true,
    "enable_auto_update": true,
    "enable_telemetry": true,
    "show_trial_reminder": true
  }
}
```

Save as: `clients/acme/config.json`

### Step 2: Prepare Client Assets

Create a client assets directory:

```
clients/acme/
├── config.json
├── logo.png (original logo)
├── splash.png (optional custom splash)
├── icon.ico (optional custom icon)
├── LICENSE.txt (client's license agreement)
├── README.txt (client-specific readme)
└── docs/ (optional custom documentation)
```

### Step 3: Run Custom Build

```bash
# Build for specific client
python build-tools/build_for_client.py --client acme --platform all

# Build for specific client and platform
python build-tools/build_for_client.py --client acme --platform windows

# Build with custom output directory
python build-tools/build_for_client.py --client acme --output dist/acme
```

---

## 🔧 Build System for Client Customization

### Custom Build Script

Create `build-tools/build_for_client.py`:

```python
"""
iTechSmart Suite - Client-Specific Build Script
Builds customized installers for specific clients
"""

import os
import sys
import json
import shutil
from pathlib import Path
from master_build import MasterBuilder

class ClientBuilder(MasterBuilder):
    """Builds customized installers for clients"""
    
    def __init__(self, client_name: str):
        super().__init__()
        self.client_name = client_name
        self.client_dir = f"clients/{client_name}"
        self.config = self.load_client_config()
        
    def load_client_config(self) -> dict:
        """Load client configuration"""
        config_file = f"{self.client_dir}/config.json"
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Client config not found: {config_file}")
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def prepare_client_assets(self):
        """Prepare client-specific assets"""
        self.log(f"Preparing assets for {self.config['client']['name']}")
        
        # Copy client logo
        client_logo = f"{self.client_dir}/{self.config['branding']['logo_file']}"
        if os.path.exists(client_logo):
            shutil.copy2(client_logo, "logo_client.png")
            
            # Convert to all required sizes
            sizes = [512, 256, 128, 64, 48, 32, 16]
            for size in sizes:
                self.run_command([
                    "convert", "logo_client.png",
                    "-resize", f"{size}x{size}",
                    f"{self.installers_dir}/assets/logo-{size}.png"
                ], f"Convert logo to {size}x{size}")
            
            # Create splash screen
            self.run_command([
                "convert", "logo_client.png",
                "-resize", "400x400",
                "-gravity", "center",
                "-background", "white",
                "-extent", "800x600",
                f"{self.installers_dir}/assets/splash/splash-screen.png"
            ], "Create splash screen")
            
            # Create icon
            self.run_command([
                "convert", "logo_client.png",
                "-resize", "256x256",
                f"{self.installers_dir}/assets/icons/client.ico"
            ], "Create icon file")
    
    def customize_source_files(self):
        """Customize source files with client information"""
        self.log("Customizing source files")
        
        replacements = {
            "iTechSmart Inc.": self.config['client']['name'],
            "iTechSmart Suite": self.config['branding']['app_name'],
            "itechsmart.dev": self.config['client']['website'].replace('https://', '').replace('http://', ''),
            "support@itechsmart.dev": self.config['client']['support_email'],
        }
        
        # Update all source files
        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    self.replace_in_file(filepath, replacements)
    
    def replace_in_file(self, filepath: str, replacements: dict):
        """Replace text in file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for old, new in replacements.items():
                content = content.replace(old, new)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            self.log(f"Error updating {filepath}: {e}", "WARNING")
    
    def build_selected_products(self):
        """Build only selected products"""
        included_products = self.config['products']['include']
        
        self.log(f"Building {len(included_products)} selected products")
        
        # Filter products
        from build_all_products import PRODUCTS
        selected = [p for p in PRODUCTS if p['id'] in included_products]
        
        # Build each selected product
        for product in selected:
            self.log(f"Building: {product['name']}")
            # Build logic here
    
    def create_client_installer(self, platform: str):
        """Create client-specific installer"""
        self.log(f"Creating installer for {self.config['client']['name']}")
        
        installer_name = self.config['branding']['installer_name']
        
        # Customize installer script
        # Platform-specific installer creation
        
    def build_for_client(self, platforms: list = None):
        """Build complete package for client"""
        if platforms is None:
            platforms = ["windows"]
        
        self.log(f"\n{'='*60}")
        self.log(f"Building Custom Package for {self.config['client']['name']}")
        self.log(f"{'='*60}")
        
        # Execute build phases
        self.phase_1_prepare_environment()
        self.prepare_client_assets()
        self.customize_source_files()
        self.phase_3_build_core_systems()
        self.phase_4_build_launcher()
        
        for platform in platforms:
            self.build_selected_products()
            self.create_client_installer(platform)
        
        self.phase_7_create_documentation()
        self.phase_8_generate_checksums()
        
        # Create client-specific distribution
        self.create_client_distribution()
        
        self.log(f"\n✅ Client package complete: {self.config['client']['name']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build client-specific package")
    parser.add_argument("--client", required=True, help="Client name")
    parser.add_argument("--platform", default="windows", help="Target platform")
    parser.add_argument("--output", help="Output directory")
    
    args = parser.parse_args()
    
    builder = ClientBuilder(args.client)
    
    platforms = [args.platform] if args.platform != "all" else ["windows", "linux", "macos"]
    
    builder.build_for_client(platforms)
```

---

## 📝 Client Configuration Examples

### Example 1: Healthcare Client

```json
{
  "client": {
    "name": "MedTech Solutions",
    "short_name": "MedTech",
    "website": "https://www.medtech-solutions.com",
    "support_email": "support@medtech-solutions.com"
  },
  "products": {
    "include": [4, 5, 13, 17, 24],
    "custom_names": {
      "iTechSmart Supreme": "MedTech Patient Management",
      "iTechSmart HL7": "MedTech HL7 Integration",
      "iTechSmart Compliance": "MedTech HIPAA Compliance"
    }
  },
  "license": {
    "types": ["trial", "professional", "enterprise"],
    "trial_days": 14
  }
}
```

### Example 2: Financial Services Client

```json
{
  "client": {
    "name": "SecureBank Financial",
    "short_name": "SecureBank",
    "website": "https://www.securebank.com",
    "support_email": "it-support@securebank.com"
  },
  "products": {
    "include": [1, 13, 15, 17, 24, 25],
    "custom_names": {
      "iTechSmart Vault": "SecureBank Vault",
      "iTechSmart Ledger": "SecureBank Blockchain Ledger",
      "iTechSmart Shield": "SecureBank Security Platform"
    }
  },
  "license": {
    "types": ["enterprise"],
    "trial_days": 0,
    "require_activation": true
  }
}
```

### Example 3: Manufacturing Client

```json
{
  "client": {
    "name": "AutoManufacture Inc.",
    "short_name": "AutoMfg",
    "website": "https://www.automanufacture.com",
    "support_email": "support@automanufacture.com"
  },
  "products": {
    "include": [1, 2, 3, 10, 18, 21, 27, 28, 29],
    "custom_names": {
      "iTechSmart Ninja": "AutoMfg AI Assistant",
      "iTechSmart Workflow": "AutoMfg Process Automation",
      "iTechSmart QA/QC": "AutoMfg Quality Control"
    }
  }
}
```

---

## 🎨 Branding Customization

### Logo Requirements

- **Format**: PNG with transparency
- **Minimum Size**: 512x512 pixels
- **Recommended**: Square aspect ratio
- **Color Mode**: RGB
- **Background**: Transparent

### Color Scheme

Customize colors in the configuration:

```json
{
  "branding": {
    "primary_color": "#0066CC",
    "secondary_color": "#FF6600",
    "accent_color": "#00CC66",
    "background_color": "#FFFFFF",
    "text_color": "#333333"
  }
}
```

---

## 🔐 License Customization

### Custom License Types

Define custom license types for clients:

```json
{
  "license": {
    "custom_types": {
      "starter": {
        "max_users": 10,
        "max_projects": 25,
        "features": ["basic_analytics", "email_support"]
      },
      "growth": {
        "max_users": 50,
        "max_projects": 100,
        "features": ["advanced_analytics", "priority_support", "api_access"]
      },
      "enterprise": {
        "max_users": -1,
        "max_projects": -1,
        "features": ["all"]
      }
    }
  }
}
```

---

## 📦 Distribution

### Client Delivery Package

Each client receives:

```
ClientName-Enterprise-Suite-v1.0.0/
├── Windows/
│   └── ClientName-Setup.exe
├── Linux/
│   ├── clientname_1.0.0_amd64.deb
│   └── clientname-1.0.0-1.x86_64.rpm
├── macOS/
│   └── ClientName.dmg
├── Documentation/
│   ├── Installation_Guide.pdf
│   ├── User_Manual.pdf
│   └── Quick_Start.pdf
├── License_Keys/
│   └── license_keys.txt
└── README.txt
```

---

## 🚀 Quick Start for Client Builds

```bash
# 1. Create client directory
mkdir -p clients/newclient

# 2. Copy template configuration
cp clients/template/config.json clients/newclient/

# 3. Add client logo
cp /path/to/client/logo.png clients/newclient/

# 4. Edit configuration
nano clients/newclient/config.json

# 5. Build for client
python build-tools/build_for_client.py --client newclient --platform all

# 6. Test installers
# Test on Windows, Linux, and macOS

# 7. Generate license keys
python src/license-system/license_manager.py generate \
  enterprise "Client Name" "client@example.com" 365

# 8. Package for delivery
python build-tools/package_for_client.py --client newclient
```

---

## ✅ Pre-Delivery Checklist

- [ ] Client logo converted to all sizes
- [ ] Company information updated in all files
- [ ] Website URLs updated
- [ ] Support email updated
- [ ] Selected products built successfully
- [ ] Installers tested on all platforms
- [ ] License keys generated
- [ ] Documentation customized
- [ ] Checksums generated
- [ ] Distribution package created
- [ ] Client approval received

---

## 📞 Support

For assistance with client customization:

- **Email**: support@itechsmart.dev
- **Website**: https://itechsmart.dev
- **Documentation**: https://docs.itechsmart.dev

---

**Copyright © 2025 iTechSmart Inc. All rights reserved.**