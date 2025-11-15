const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  selectScript: () => ipcRenderer.invoke('select-script'),
  showMessage: (opts) => ipcRenderer.invoke('show-message', opts),
  runInstaller: (payload) => ipcRenderer.invoke('run-installer', payload)
});
