import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electron', {
  // Docker operations
  checkDockerInstalled: () => ipcRenderer.invoke('docker:check-installed'),
  installDocker: () => ipcRenderer.invoke('docker:install'),
  
  // Product operations
  startProduct: (productId: string) => ipcRenderer.invoke('product:start', productId),
  stopProduct: (productId: string) => ipcRenderer.invoke('product:stop', productId),
  restartProduct: (productId: string) => ipcRenderer.invoke('product:restart', productId),
  getProductStatus: (productId: string) => ipcRenderer.invoke('product:status', productId),
  openProduct: (productId: string) => ipcRenderer.invoke('product:open', productId),
  
  // Products list
  getProducts: () => ipcRenderer.invoke('products:list'),
  getAllProductStatuses: () => ipcRenderer.invoke('products:status-all'),
  
  // License operations
  getLicense: () => ipcRenderer.invoke('license:get'),
  activateLicense: (licenseKey: string) => ipcRenderer.invoke('license:activate', licenseKey),
  validateLicense: () => ipcRenderer.invoke('license:validate'),
  canAccessProduct: (productId: string) => ipcRenderer.invoke('license:can-access-product', productId),
  
  // Update operations
  checkForUpdates: () => ipcRenderer.invoke('update:check'),
  downloadUpdate: () => ipcRenderer.invoke('update:download'),
  installUpdate: () => ipcRenderer.invoke('update:install'),
  
  // System operations
  getSystemInfo: () => ipcRenderer.invoke('system:info'),
  getAppVersion: () => ipcRenderer.invoke('app:version'),
  quitApp: () => ipcRenderer.invoke('app:quit'),
  
  // Event listeners
  on: (channel: string, callback: Function) => {
    ipcRenderer.on(channel, (_, ...args) => callback(...args));
  },
  
  removeListener: (channel: string, callback: Function) => {
    ipcRenderer.removeListener(channel, callback as any);
  }
});

// TypeScript declarations
declare global {
  interface Window {
    electron: {
      checkDockerInstalled: () => Promise<boolean>;
      installDocker: () => Promise<boolean>;
      startProduct: (productId: string) => Promise<boolean>;
      stopProduct: (productId: string) => Promise<boolean>;
      restartProduct: (productId: string) => Promise<boolean>;
      getProductStatus: (productId: string) => Promise<'running' | 'stopped' | 'error'>;
      openProduct: (productId: string) => Promise<void>;
      getProducts: () => Promise<any[]>;
      getAllProductStatuses: () => Promise<Record<string, string>>;
      getLicense: () => Promise<any>;
      activateLicense: (licenseKey: string) => Promise<{ success: boolean; message: string }>;
      validateLicense: () => Promise<boolean>;
      canAccessProduct: (productId: string) => Promise<boolean>;
      checkForUpdates: () => Promise<boolean>;
      downloadUpdate: () => Promise<boolean>;
      installUpdate: () => Promise<void>;
      getSystemInfo: () => Promise<any>;
      getAppVersion: () => Promise<string>;
      quitApp: () => Promise<void>;
      on: (channel: string, callback: Function) => void;
      removeListener: (channel: string, callback: Function) => void;
    };
  }
}