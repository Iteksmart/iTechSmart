# ProofLink.AI Browser Extension

Create cryptographic proofs of any file or webpage instantly with the ProofLink.AI browser extension.

## Features

- 🔒 **One-Click Proof Creation** - Create proofs of any webpage with a single click
- ✂️ **Selection Proofs** - Create proofs of selected text
- 🖼️ **Image Proofs** - Right-click any image to create a proof
- 🔗 **Link Proofs** - Create proofs of links
- ✓ **Instant Verification** - Verify proofs from clipboard
- ⌨️ **Keyboard Shortcuts** - Quick access with Ctrl+Shift+P and Ctrl+Shift+V
- 📊 **Stats Dashboard** - Track your proof creation activity
- 🎨 **Beautiful UI** - Modern, intuitive interface
- 🔔 **Notifications** - Real-time feedback on proof creation
- ⚙️ **Customizable Settings** - Configure API endpoint, notifications, and more

## Installation

### Chrome / Edge / Brave

1. Download or clone this repository
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" in the top right
4. Click "Load unpacked"
5. Select the `browser-extension` folder
6. The ProofLink.AI icon should appear in your toolbar

### Firefox

1. Download or clone this repository
2. Open Firefox and navigate to `about:debugging#/runtime/this-firefox`
3. Click "Load Temporary Add-on"
4. Navigate to the `browser-extension` folder
5. Select the `manifest.json` file
6. The ProofLink.AI icon should appear in your toolbar

## Usage

### Creating Proofs

#### Method 1: Extension Popup
1. Click the ProofLink.AI icon in your toolbar
2. Choose from:
   - **Proof This Page** - Create proof of entire webpage
   - **Proof Selection** - Create proof of selected text
   - **Verify Proof** - Verify a proof from clipboard

#### Method 2: Context Menu
1. Right-click anywhere on a webpage
2. Select "Create Proof of This Page"
3. Or right-click on:
   - Selected text → "Create Proof of Selection"
   - Images → "Create Proof of This Image"
   - Links → "Create Proof of This Link"

#### Method 3: Keyboard Shortcuts
- **Ctrl+Shift+P** (Cmd+Shift+P on Mac) - Create proof of current page
- **Ctrl+Shift+V** (Cmd+Shift+V on Mac) - Verify proof from clipboard

### Verifying Proofs

1. Copy a proof link to your clipboard
2. Click the extension icon
3. Click "Verify Proof"
4. Or use keyboard shortcut: Ctrl+Shift+V

The extension will verify the proof and show you:
- ✓ Valid - Proof is authentic
- ✗ Invalid - Proof could not be verified

### Settings

Click the settings icon in the extension popup to configure:

- **API URL** - Change to use a custom API endpoint
- **API Key** - For advanced users with API key authentication
- **Notifications** - Enable/disable notifications
- **Auto-copy** - Automatically copy proof links to clipboard
- **Analytics** - Send anonymous usage data

## Features in Detail

### Context Menu Integration

The extension adds 5 context menu items:

1. **Create Proof of This Page** - Available on any page
2. **Create Proof of Selection** - Available when text is selected
3. **Create Proof of This Image** - Available when right-clicking images
4. **Create Proof of This Link** - Available when right-clicking links
5. **Verify Proof from Clipboard** - Available on any page

### Keyboard Shortcuts

- **Create Proof**: Ctrl+Shift+P (Cmd+Shift+P on Mac)
- **Verify Proof**: Ctrl+Shift+V (Cmd+Shift+V on Mac)

### Popup Dashboard

The extension popup shows:

- **Quick Actions** - One-click buttons for common tasks
- **Stats** - Total proofs and monthly count
- **Recent Proofs** - List of your 5 most recent proofs
- **Status** - Connection status indicator

### Notifications

The extension shows notifications for:

- ✓ Proof created successfully
- ✗ Proof creation failed
- ✓ Proof verified successfully
- ✗ Proof verification failed

### Auto-Copy

When enabled, proof links are automatically copied to your clipboard after creation.

## API Configuration

### Default API
By default, the extension connects to:
```
https://api.prooflink.ai/api/v1
```

### Custom API
To use a custom API endpoint:

1. Click the extension icon
2. Click the settings icon
3. Enter your API URL
4. Click "Save Settings"

### Local Development
For local development, use:
```
http://localhost:8000/api/v1
```

## Authentication

### Sign In
1. Click the extension icon
2. Click "Sign In"
3. You'll be redirected to the ProofLink.AI login page
4. After signing in, return to the extension

### Sign Out
1. Click the extension icon
2. Click the settings icon
3. Click "Sign Out"

## Privacy

The extension:

- ✓ Only sends data when you create or verify proofs
- ✓ Does not track your browsing history
- ✓ Does not collect personal information
- ✓ Uses secure HTTPS connections
- ✓ Stores authentication tokens locally

Optional analytics:
- ✗ Can be disabled in settings
- ✗ Only sends anonymous usage statistics
- ✗ No personal data is collected

## Troubleshooting

### Extension Not Working

1. Check that you're signed in
2. Verify API URL in settings
3. Check browser console for errors
4. Try reloading the extension

### Proof Creation Fails

1. Check internet connection
2. Verify you're signed in
3. Check API status at https://status.prooflink.ai
4. Try again in a few moments

### Verification Fails

1. Ensure proof link is copied correctly
2. Check that proof link is valid
3. Try copying the link again
4. Contact support if issue persists

## Support

- **Email**: support@prooflink.ai
- **Website**: https://prooflink.ai
- **Documentation**: https://docs.prooflink.ai
- **Status**: https://status.prooflink.ai

## Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/your-org/prooflink.git
cd prooflink/browser-extension

# No build step required - extension is ready to use
```

### File Structure

```
browser-extension/
├── manifest.json           # Extension manifest
├── background/
│   └── service-worker.js  # Background service worker
├── content/
│   ├── content-script.js  # Content script
│   └── content-styles.css # Content styles
├── popup/
│   ├── popup.html         # Popup interface
│   ├── popup.css          # Popup styles
│   └── popup.js           # Popup logic
├── options/
│   ├── options.html       # Settings page
│   ├── options.css        # Settings styles
│   └── options.js         # Settings logic
└── icons/
    ├── icon16.png         # 16x16 icon
    ├── icon32.png         # 32x32 icon
    ├── icon48.png         # 48x48 icon
    └── icon128.png        # 128x128 icon
```

## License

Copyright © 2025 ProofLink.AI. All rights reserved.

## Version History

### v1.2.0 (2025-01-15)
- Initial release
- Context menu integration
- Keyboard shortcuts
- Popup dashboard
- Settings page
- Notifications
- Auto-copy feature