// ProofLink.AI Browser Extension - Options Page Script

const API_URL = 'https://api.prooflink.ai/api/v1';

// DOM Elements
const apiUrlInput = document.getElementById('api-url');
const apiKeyInput = document.getElementById('api-key');
const notificationsEnabled = document.getElementById('notifications-enabled');
const autoCopy = document.getElementById('auto-copy');
const analytics = document.getElementById('analytics');
const accountInfo = document.getElementById('account-info');
const logoutBtn = document.getElementById('logout-btn');
const saveBtn = document.getElementById('save-btn');
const resetBtn = document.getElementById('reset-btn');
const statusMessage = document.getElementById('status-message');

// Default settings
const defaultSettings = {
  apiUrl: 'https://api.prooflink.ai/api/v1',
  apiKey: '',
  notificationsEnabled: true,
  autoCopy: true,
  analytics: true
};

// Load settings on page load
async function loadSettings() {
  try {
    const settings = await chrome.storage.sync.get(defaultSettings);
    
    apiUrlInput.value = settings.apiUrl;
    apiKeyInput.value = settings.apiKey;
    notificationsEnabled.checked = settings.notificationsEnabled;
    autoCopy.checked = settings.autoCopy;
    analytics.checked = settings.analytics;
    
    // Load account info
    await loadAccountInfo();
  } catch (error) {
    console.error('Error loading settings:', error);
    showStatus('Failed to load settings', 'error');
  }
}

// Load account information
async function loadAccountInfo() {
  try {
    const { token } = await chrome.runtime.sendMessage({ action: 'getAuthToken' });
    
    if (!token) {
      accountInfo.innerHTML = `
        <p>Not signed in</p>
        <p class="help-text">Sign in to sync your proofs across devices</p>
      `;
      logoutBtn.style.display = 'none';
      return;
    }
    
    const response = await fetch(`${API_URL}/users/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.ok) {
      const user = await response.json();
      accountInfo.innerHTML = `
        <p><strong>Email:</strong> ${user.email}</p>
        <p><strong>Plan:</strong> ${user.subscription_tier || 'Free'}</p>
        <p><strong>Member since:</strong> ${new Date(user.created_at).toLocaleDateString()}</p>
      `;
      logoutBtn.style.display = 'block';
    } else {
      accountInfo.innerHTML = `
        <p>Failed to load account information</p>
      `;
      logoutBtn.style.display = 'none';
    }
  } catch (error) {
    console.error('Error loading account info:', error);
    accountInfo.innerHTML = `
      <p>Not signed in</p>
      <p class="help-text">Sign in to sync your proofs across devices</p>
    `;
    logoutBtn.style.display = 'none';
  }
}

// Save settings
async function saveSettings() {
  try {
    const settings = {
      apiUrl: apiUrlInput.value.trim() || defaultSettings.apiUrl,
      apiKey: apiKeyInput.value.trim(),
      notificationsEnabled: notificationsEnabled.checked,
      autoCopy: autoCopy.checked,
      analytics: analytics.checked
    };
    
    await chrome.storage.sync.set(settings);
    
    // Update background script
    chrome.runtime.sendMessage({
      action: 'updateSettings',
      settings
    });
    
    showStatus('Settings saved successfully!', 'success');
  } catch (error) {
    console.error('Error saving settings:', error);
    showStatus('Failed to save settings', 'error');
  }
}

// Reset to defaults
async function resetSettings() {
  if (!confirm('Are you sure you want to reset all settings to defaults?')) {
    return;
  }
  
  try {
    await chrome.storage.sync.set(defaultSettings);
    
    apiUrlInput.value = defaultSettings.apiUrl;
    apiKeyInput.value = defaultSettings.apiKey;
    notificationsEnabled.checked = defaultSettings.notificationsEnabled;
    autoCopy.checked = defaultSettings.autoCopy;
    analytics.checked = defaultSettings.analytics;
    
    showStatus('Settings reset to defaults', 'success');
  } catch (error) {
    console.error('Error resetting settings:', error);
    showStatus('Failed to reset settings', 'error');
  }
}

// Logout
async function logout() {
  if (!confirm('Are you sure you want to sign out?')) {
    return;
  }
  
  try {
    await chrome.runtime.sendMessage({ action: 'logout' });
    await loadAccountInfo();
    showStatus('Signed out successfully', 'success');
  } catch (error) {
    console.error('Error signing out:', error);
    showStatus('Failed to sign out', 'error');
  }
}

// Show status message
function showStatus(message, type) {
  statusMessage.textContent = message;
  statusMessage.className = `status-message ${type}`;
  
  setTimeout(() => {
    statusMessage.className = 'status-message';
  }, 3000);
}

// Event Listeners
saveBtn.addEventListener('click', saveSettings);
resetBtn.addEventListener('click', resetSettings);
logoutBtn.addEventListener('click', logout);

// Auto-save on input change
apiUrlInput.addEventListener('change', saveSettings);
apiKeyInput.addEventListener('change', saveSettings);
notificationsEnabled.addEventListener('change', saveSettings);
autoCopy.addEventListener('change', saveSettings);
analytics.addEventListener('change', saveSettings);

// Initialize on load
loadSettings();