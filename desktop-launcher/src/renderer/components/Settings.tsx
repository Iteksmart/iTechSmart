import React, { useState, useEffect } from 'react';
import { Info, HardDrive, Cpu, Database, RefreshCw, Download } from 'lucide-react';

function Settings() {
  const [systemInfo, setSystemInfo] = useState<any>(null);
  const [appVersion, setAppVersion] = useState<string>('');
  const [checkingUpdates, setCheckingUpdates] = useState(false);
  const [updateAvailable, setUpdateAvailable] = useState(false);

  useEffect(() => {
    loadSystemInfo();
    loadAppVersion();
  }, []);

  const loadSystemInfo = async () => {
    try {
      const info = await window.electron.getSystemInfo();
      setSystemInfo(info);
    } catch (error) {
      console.error('Failed to load system info:', error);
    }
  };

  const loadAppVersion = async () => {
    try {
      const version = await window.electron.getAppVersion();
      setAppVersion(version);
    } catch (error) {
      console.error('Failed to load app version:', error);
    }
  };

  const handleCheckUpdates = async () => {
    setCheckingUpdates(true);
    try {
      const available = await window.electron.checkForUpdates();
      setUpdateAvailable(available);
    } catch (error) {
      console.error('Failed to check for updates:', error);
    } finally {
      setCheckingUpdates(false);
    }
  };

  const handleDownloadUpdate = async () => {
    try {
      await window.electron.downloadUpdate();
    } catch (error) {
      console.error('Failed to download update:', error);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-100">Settings</h1>
        <p className="text-slate-400 mt-1">Manage your iTechSmart Suite configuration</p>
      </div>

      {/* Application Info */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center space-x-3 mb-2">
            <Info size={24} className="text-blue-400" />
            <h2 className="text-xl font-bold text-slate-100">Application</h2>
          </div>
        </div>
        
        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-slate-400">Version</div>
              <div className="text-lg font-semibold text-slate-200">{appVersion || 'Loading...'}</div>
            </div>
            <button
              onClick={handleCheckUpdates}
              disabled={checkingUpdates}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw size={16} className={checkingUpdates ? 'animate-spin' : ''} />
              <span>Check for Updates</span>
            </button>
          </div>

          {updateAvailable && (
            <div className="p-4 bg-green-900/20 border border-green-700/30 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-400 font-medium">Update Available!</p>
                  <p className="text-sm text-slate-400 mt-1">A new version is ready to download</p>
                </div>
                <button
                  onClick={handleDownloadUpdate}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                >
                  <Download size={16} />
                  <span>Download</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* System Information */}
      {systemInfo && (
        <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
          <div className="p-6 border-b border-slate-700">
            <div className="flex items-center space-x-3 mb-2">
              <HardDrive size={24} className="text-blue-400" />
              <h2 className="text-xl font-bold text-slate-100">System Information</h2>
            </div>
          </div>
          
          <div className="p-6 space-y-6">
            {/* CPU */}
            {systemInfo.cpu && (
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <Cpu size={20} className="text-slate-400" />
                  <h3 className="font-semibold text-slate-200">CPU</h3>
                </div>
                <div className="grid grid-cols-2 gap-4 pl-7">
                  <div>
                    <div className="text-xs text-slate-500">Brand</div>
                    <div className="text-sm text-slate-300">{systemInfo.cpu.brand}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Cores</div>
                    <div className="text-sm text-slate-300">{systemInfo.cpu.cores}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Speed</div>
                    <div className="text-sm text-slate-300">{systemInfo.cpu.speed} GHz</div>
                  </div>
                </div>
              </div>
            )}

            {/* Memory */}
            {systemInfo.memory && (
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <Database size={20} className="text-slate-400" />
                  <h3 className="font-semibold text-slate-200">Memory</h3>
                </div>
                <div className="grid grid-cols-2 gap-4 pl-7">
                  <div>
                    <div className="text-xs text-slate-500">Total</div>
                    <div className="text-sm text-slate-300">{formatBytes(systemInfo.memory.total)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Used</div>
                    <div className="text-sm text-slate-300">{formatBytes(systemInfo.memory.used)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Free</div>
                    <div className="text-sm text-slate-300">{formatBytes(systemInfo.memory.free)}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Docker */}
            {systemInfo.docker && (
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <HardDrive size={20} className="text-slate-400" />
                  <h3 className="font-semibold text-slate-200">Docker</h3>
                </div>
                <div className="grid grid-cols-2 gap-4 pl-7">
                  <div>
                    <div className="text-xs text-slate-500">Containers</div>
                    <div className="text-sm text-slate-300">{systemInfo.docker.containers}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Running</div>
                    <div className="text-sm text-green-400">{systemInfo.docker.containersRunning}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Stopped</div>
                    <div className="text-sm text-slate-300">{systemInfo.docker.containersStopped}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Images</div>
                    <div className="text-sm text-slate-300">{systemInfo.docker.images}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* About */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
        <h3 className="font-semibold text-slate-200 mb-4">About iTechSmart Suite</h3>
        <p className="text-sm text-slate-400 mb-4">
          iTechSmart Suite is a comprehensive collection of 35 enterprise-grade applications for
          IT management, automation, security, and operations.
        </p>
        <div className="flex items-center space-x-4 text-sm text-slate-500">
          <a href="#" className="hover:text-blue-400 transition-colors">Documentation</a>
          <span>•</span>
          <a href="#" className="hover:text-blue-400 transition-colors">Support</a>
          <span>•</span>
          <a href="#" className="hover:text-blue-400 transition-colors">GitHub</a>
        </div>
      </div>
    </div>
  );
}

export default Settings;