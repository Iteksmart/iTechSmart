import { autoUpdater } from 'electron-updater';
import { app, dialog } from 'electron';
import Store from 'electron-store';

export class UpdateManager {
  private store: Store;
  private updateAvailable: boolean = false;

  constructor() {
    this.store = new Store();
    this.setupAutoUpdater();
  }

  private setupAutoUpdater() {
    // Configure auto-updater
    autoUpdater.autoDownload = false;
    autoUpdater.autoInstallOnAppQuit = true;

    // Update available
    autoUpdater.on('update-available', (info) => {
      this.updateAvailable = true;
      console.log('Update available:', info);
    });

    // Update not available
    autoUpdater.on('update-not-available', (info) => {
      this.updateAvailable = false;
      console.log('Update not available:', info);
    });

    // Download progress
    autoUpdater.on('download-progress', (progress) => {
      console.log('Download progress:', progress);
    });

    // Update downloaded
    autoUpdater.on('update-downloaded', (info) => {
      console.log('Update downloaded:', info);
      
      dialog.showMessageBox({
        type: 'info',
        title: 'Update Ready',
        message: 'A new version has been downloaded. Restart the application to apply the updates.',
        buttons: ['Restart', 'Later']
      }).then((result) => {
        if (result.response === 0) {
          autoUpdater.quitAndInstall();
        }
      });
    });

    // Error
    autoUpdater.on('error', (error) => {
      console.error('Update error:', error);
    });
  }

  /**
   * Check for updates
   */
  async checkForUpdates(): Promise<boolean> {
    try {
      const result = await autoUpdater.checkForUpdates();
      return result !== null;
    } catch (error) {
      console.error('Failed to check for updates:', error);
      return false;
    }
  }

  /**
   * Download update
   */
  async downloadUpdate(): Promise<boolean> {
    try {
      if (!this.updateAvailable) {
        return false;
      }

      await autoUpdater.downloadUpdate();
      return true;
    } catch (error) {
      console.error('Failed to download update:', error);
      return false;
    }
  }

  /**
   * Install update
   */
  installUpdate(): void {
    autoUpdater.quitAndInstall();
  }

  /**
   * Get update info
   */
  isUpdateAvailable(): boolean {
    return this.updateAvailable;
  }
}