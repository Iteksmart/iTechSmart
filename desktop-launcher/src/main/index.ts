import { app, BrowserWindow, ipcMain, Tray, Menu, shell } from 'electron';
import path from 'path';
import { DockerManager } from './docker-manager';
import { LicenseManager } from './license-manager';
import { UpdateManager } from './update-manager';
import { systemAgentsManager } from './system-agents-manager';
import { PRODUCTS } from './products';

let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;
let dockerManager: DockerManager;
let licenseManager: LicenseManager;
let updateManager: UpdateManager;
let isQuitting = false;

const isDev = process.env.NODE_ENV === 'development';

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../../assets/icons/icon.png'),
    title: 'iTechSmart Suite',
    show: false
  });

  // Load the app
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow?.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function createTray() {
  tray = new Tray(path.join(__dirname, '../../assets/icons/tray-icon.png'));
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show iTechSmart Suite',
      click: () => {
        mainWindow?.show();
      }
    },
    { type: 'separator' },
    {
      label: 'Running Products',
      submenu: []
    },
    { type: 'separator' },
    {
      label: 'Check for Updates',
      click: async () => {
        await updateManager.checkForUpdates();
      }
    },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip('iTechSmart Suite');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    mainWindow?.show();
  });
}

// Initialize managers
async function initializeManagers() {
  dockerManager = new DockerManager();
  licenseManager = new LicenseManager();
  updateManager = new UpdateManager();

  // Check Docker installation
  const dockerInstalled = await dockerManager.checkDockerInstalled();
  if (!dockerInstalled) {
    // Show dialog to install Docker
    mainWindow?.webContents.send('docker-not-installed');
  }

  // Validate license
  const licenseValid = await licenseManager.validateLicense();
  if (!licenseValid) {
    mainWindow?.webContents.send('license-invalid');
  }

  // Check for updates
  await updateManager.checkForUpdates();
}

// IPC Handlers

// Docker operations
ipcMain.handle('docker:check-installed', async () => {
  return await dockerManager.checkDockerInstalled();
});

ipcMain.handle('docker:install', async () => {
  return await dockerManager.installDocker();
});

ipcMain.handle('product:start', async (_, productId: string) => {
  return await dockerManager.startProduct(productId);
});

ipcMain.handle('product:stop', async (_, productId: string) => {
  return await dockerManager.stopProduct(productId);
});

ipcMain.handle('product:restart', async (_, productId: string) => {
  await dockerManager.stopProduct(productId);
  return await dockerManager.startProduct(productId);
});

ipcMain.handle('product:status', async (_, productId: string) => {
  return await dockerManager.getProductStatus(productId);
});

ipcMain.handle('product:open', async (_, productId: string) => {
  const product = PRODUCTS.find(p => p.id === productId);
  if (product) {
    await shell.openExternal(`http://localhost:${product.frontendPort}`);
  }
});

ipcMain.handle('products:list', async () => {
  return PRODUCTS;
});

ipcMain.handle('products:status-all', async () => {
  const statuses: Record<string, string> = {};
  for (const product of PRODUCTS) {
    statuses[product.id] = await dockerManager.getProductStatus(product.id);
  }
  return statuses;
});

// License operations
ipcMain.handle('license:get', async () => {
  return licenseManager.getLicense();
});

ipcMain.handle('license:activate', async (_, licenseKey: string) => {
  return await licenseManager.activateLicense(licenseKey);
});

ipcMain.handle('license:validate', async () => {
  return await licenseManager.validateLicense();
});

ipcMain.handle('license:can-access-product', async (_, productId: string) => {
  return licenseManager.canAccessProduct(productId);
});

// Update operations
ipcMain.handle('update:check', async () => {
  return await updateManager.checkForUpdates();
});

ipcMain.handle('update:download', async () => {
  return await updateManager.downloadUpdate();
});

ipcMain.handle('update:install', async () => {
  return await updateManager.installUpdate();
});

// System operations
ipcMain.handle('system:info', async () => {
  return await dockerManager.getSystemInfo();
});

ipcMain.handle('app:version', () => {
  return app.getVersion();
});

ipcMain.handle('app:quit', () => {
  isQuitting = true;
  app.quit();
});

// App lifecycle
app.whenReady().then(async () => {
  createWindow();
  createTray();
  await initializeManagers();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
});

// System Agents IPC Handlers
ipcMain.handle('agents:get-all', async () => {
  try {
    return await systemAgentsManager.getAgents();
  } catch (error) {
    console.error('Failed to get agents:', error);
    throw error;
  }
});

ipcMain.handle('agents:get', async (_, agentId: string) => {
  try {
    return await systemAgentsManager.getAgent(agentId);
  } catch (error) {
    console.error(`Failed to get agent ${agentId}:`, error);
    throw error;
  }
});

ipcMain.handle('agents:get-metrics', async (_, agentId: string) => {
  try {
    return await systemAgentsManager.getSystemMetrics(agentId);
  } catch (error) {
    console.error(`Failed to get metrics for agent ${agentId}:`, error);
    throw error;
  }
});

ipcMain.handle('agents:get-alerts', async (_, agentId: string) => {
  try {
    return await systemAgentsManager.getAgentAlerts(agentId);
  } catch (error) {
    console.error(`Failed to get alerts for agent ${agentId}:`, error);
    throw error;
  }
});

ipcMain.handle('agents:resolve-alert', async (_, agentId: string, alertId: string) => {
  try {
    await systemAgentsManager.resolveAlert(agentId, alertId);
    return { success: true };
  } catch (error) {
    console.error(`Failed to resolve alert ${alertId}:`, error);
    throw error;
  }
});

ipcMain.handle('agents:execute-command', async (_, agentId: string, command: string, parameters?: any) => {
  try {
    return await systemAgentsManager.executeCommand(agentId, command, parameters);
  } catch (error) {
    console.error(`Failed to execute command on agent ${agentId}:`, error);
    throw error;
  }
});

ipcMain.handle('agents:get-stats', async () => {
  try {
    return await systemAgentsManager.getAgentStats();
  } catch (error) {
    console.error('Failed to get agent stats:', error);
    throw error;
  }
});

ipcMain.handle('agents:get-health-score', async () => {
  try {
    return await systemAgentsManager.getSystemHealthScore();
  } catch (error) {
    console.error('Failed to get health score:', error);
    return 0;
  }
});

ipcMain.handle('agents:has-critical-alerts', async () => {
  try {
    return await systemAgentsManager.hasCriticalAlerts();
  } catch (error) {
    console.error('Failed to check critical alerts:', error);
    return false;
  }
});

ipcMain.handle('agents:get-tray-status', async () => {
  try {
    return await systemAgentsManager.getSystemTrayStatus();
  } catch (error) {
    console.error('Failed to get tray status:', error);
    return 'Status unavailable';
  }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
});

process.on('unhandledRejection', (error) => {
  console.error('Unhandled rejection:', error);
});