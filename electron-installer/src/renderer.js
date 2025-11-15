const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const sudo = require('sudo-prompt');
const os = require('os');

const defaultScript = path.resolve(__dirname, '..', '..', 'hardened_docker_install.sh');
let chosenScript = defaultScript;

const btnSelect = document.getElementById('btn-select');
const scriptPathElem = document.getElementById('script-path');
const envText = document.getElementById('env-text');
const btnRun = document.getElementById('btn-run');
const logEl = document.getElementById('log');

scriptPathElem.innerText = chosenScript;

btnSelect.addEventListener('click', async () => {
  const p = await window.electronAPI.selectScript();
  if (p) {
    chosenScript = p;
    scriptPathElem.innerText = chosenScript;
  }
});

function appendLog(line) {
  logEl.textContent += '\n' + line;
  logEl.scrollTop = logEl.scrollHeight;
}

btnRun.addEventListener('click', async () => {
  // write env to temp file
  const envContent = envText.value || '';
  const tmpDir = os.tmpdir();
  const envPath = path.join(tmpDir, `itechsmart_env_${Date.now()}.env`);
  fs.writeFileSync(envPath, envContent, { mode: 0o600 });
  appendLog(`Wrote env file to ${envPath}`);

  // build command to run: ensure script is executable
  try {
    fs.chmodSync(chosenScript, 0o755);
  } catch (e) {
    appendLog('Failed to chmod script: ' + String(e));
  }

  // Copy temp env next to script's directory
  const scriptDir = path.dirname(chosenScript);
  const destEnv = path.join(scriptDir, '.env');
  try {
    fs.copyFileSync(envPath, destEnv);
    appendLog(`Copied env to ${destEnv}`);
  } catch (e) {
    appendLog('Failed to copy env: ' + String(e));
  }

  const cmd = `bash "${chosenScript}"`;
  appendLog('Running installer with elevation...');

  const opts = { name: 'iTechSmart Installer' };
  sudo.exec(cmd, opts, (error, stdout, stderr) => {
    if (error) {
      appendLog('Installer error: ' + error);
      window.electronAPI.showMessage({
        type: 'error',
        title: 'Installation failed',
        message: String(error)
      });
      return;
    }
    if (stdout) appendLog('STDOUT:\n' + stdout);
    if (stderr) appendLog('STDERR:\n' + stderr);
    appendLog('Installer finished.');
    window.electronAPI.showMessage({
      type: 'info',
      title: 'Installer finished',
      message: 'Installation completed. Check logs in installer application.'
    });
  });
});
