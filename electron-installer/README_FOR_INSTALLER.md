# iTechSmart Electron Installer

## Prerequisites
- Node.js (18+ recommended)
- npm or yarn
- Your project root should contain `hardened_docker_install.sh` (bundled) or point the GUI to a script

## Setup
1. Copy this `electron-installer` folder into your project root next to `hardened_docker_install.sh` (the installer will use the bundled script by default).
2. From inside `electron-installer` run:
   ```bash
   npm install
   npm run start
   ```
   This will open the installer UI.

## Build distributables
- To create platform-specific installers (requires native toolchains):
  ```bash
  npm run dist
  ```
  - On macOS to build `.dmg`/`.pkg` you need Xcode tooling.
  - On Windows you need to run the build on Windows to produce `.exe` (recommended), or use cross-compilation CI images.
  - For Linux AppImage and .deb, build on Linux.

## Security notes
- The UI writes `.env` into the same folder as the script before running it. You can change this behaviour to pass env via stdin or other secure mechanisms.
- `sudo-prompt` elevates and runs the script; review the script before bundling.
