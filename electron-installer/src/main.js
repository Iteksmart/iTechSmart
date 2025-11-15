const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const isDev = process.env.ELECTRON_DEV === '1' || process.env.NODE_ENV === 'development';

function createWindow() {
  const win = new BrowserWindow({
    width: 780,
    height: 640,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      sandbox: false
    },
    resizable: false
  });

  win.loadFile(path.join(__dirname, 'index.html'));
  if (isDev) win.webContents.openDevTools({ mode: 'detach' });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

// IPC handlers
ipcMain.handle('select-script', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters: [{ name: 'Shell Scripts', extensions: ['sh', 'bat', 'ps1'] }]
  });
  if (canceled) return null;
  return filePaths[0];
});

ipcMain.handle('show-message', (ev, opts) => {
  dialog.showMessageBox(opts);
});
