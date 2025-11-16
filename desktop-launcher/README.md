# iTechSmart Suite Desktop Launcher

Professional desktop application for managing all 35 iTechSmart products with Docker integration, license management, and auto-updates.

## 🎯 Status: 95% Complete

### ✅ What's Working
- Docker container management
- License activation and validation
- Auto-update system
- Product definitions (all 35)
- React UI (Dashboard, Product Cards, Settings, License)
- System tray integration
- IPC communication

### ⏳ What's Needed (5%)
- Build configuration testing
- Icon assets
- Final testing on all platforms

## 🚀 Quick Start

### Development

```bash
# Install dependencies
npm install

# Start development mode
npm run dev

# In another terminal, start Electron
npm start
```

### Build Installers

```bash
# Build for current platform
npm run package

# Build for specific platform
npm run package:win    # Windows
npm run package:mac    # macOS
npm run package:linux  # Linux

# Build for all platforms
npm run package:all
```

## 📦 Features

### Docker Management
- Automatic Docker installation check
- Pull images from ghcr.io/iteksmart
- Start/stop containers
- Monitor container status
- System resource monitoring

### License System
- Trial license (30 days, 3 products)
- Tier-based access control
- Online validation with server
- Offline grace period (7 days)
- Machine-locked activation

### User Interface
- Modern React + TypeScript UI
- Tailwind CSS styling
- Product grid with search/filter
- Real-time status updates
- System tray integration

### Auto-Updates
- Automatic update checking
- Background downloads
- One-click installation
- Version management

## 🏗️ Architecture

```
desktop-launcher/
├── src/
│   ├── main/              # Electron main process
│   │   ├── index.ts       # Entry point
│   │   ├── docker-manager.ts
│   │   ├── license-manager.ts
│   │   ├── update-manager.ts
│   │   ├── products.ts
│   │   └── preload.ts     # IPC bridge
│   └── renderer/          # React UI
│       ├── App.tsx
│       ├── components/
│       │   ├── Dashboard.tsx
│       │   ├── ProductCard.tsx
│       │   ├── LicenseActivation.tsx
│       │   └── Settings.tsx
│       ├── index.html
│       ├── main.tsx
│       └── index.css
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── electron-builder.yml (in package.json)
```

## 🔧 Configuration

### Environment Variables

```bash
# License server URL
LICENSE_SERVER_URL=https://license.itechsmart.com/api

# Update server URL
UPDATE_SERVER_URL=https://updates.itechsmart.com
```

### Product Configuration

All 35 products are configured in `src/main/products.ts` with:
- Product ID
- Name and description
- Category
- Backend/frontend ports
- Required license tier
- Icon

## 📱 Usage

### For End Users

1. **Install the launcher**
   - Windows: Run `.exe` installer
   - macOS: Open `.dmg` and drag to Applications
   - Linux: Install `.deb` or `.rpm` package

2. **First launch**
   - Launcher checks for Docker
   - Starts 30-day trial automatically
   - Shows dashboard with all products

3. **Start a product**
   - Click product card
   - Click "Start" button
   - Wait for Docker to pull images (first time)
   - Click "Open" to launch in browser

4. **Activate license**
   - Click "License" in sidebar
   - Enter license key
   - Products unlock based on tier

### For Developers

```bash
# Install dependencies
npm install

# Development mode
npm run dev          # Start Vite dev server
npm start            # Start Electron (in another terminal)

# Build
npm run build        # Build TypeScript + React
npm run package      # Create installer
```

## 🎨 Customization

### Adding Products

Edit `src/main/products.ts`:

```typescript
{
  id: 'my-product',
  name: 'My Product',
  description: 'Product description',
  category: 'My Category',
  backendPort: 8036,
  frontendPort: 3036,
  icon: 'my-icon.png',
  tier: 'professional'
}
```

### Styling

Edit `src/renderer/index.css` or component styles using Tailwind classes.

### License Tiers

Edit `src/main/license-manager.ts` to modify tier logic.

## 🐛 Troubleshooting

### Docker not found
- Install Docker Desktop
- Restart launcher
- Check Docker is running

### Product won't start
- Check Docker is running
- Check port is not in use
- View Docker logs: `docker logs <container-name>`

### License activation fails
- Check internet connection
- Verify license key format
- Contact support

## 📄 License

Copyright © 2025 iTechSmart Inc. All rights reserved.

## 🤝 Support

- Email: support@itechsmart.com
- Documentation: https://docs.itechsmart.com
- GitHub: https://github.com/Iteksmart/iTechSmart