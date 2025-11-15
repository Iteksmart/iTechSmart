// ProofLink.AI Browser Extension - Popup Script

const API_URL = 'https://api.prooflink.ai/api/v1';

// DOM Elements
const authSection = document.getElementById('auth-section');
const mainSection = document.getElementById('main-section');
const loginBtn = document.getElementById('login-btn');
const registerBtn = document.getElementById('register-btn');
const proofPageBtn = document.getElementById('proof-page-btn');
const proofSelectionBtn = document.getElementById('proof-selection-btn');
const verifyBtn = document.getElementById('verify-btn');
const settingsBtn = document.getElementById('settings-btn');
const dashboardBtn = document.getElementById('dashboard-btn');
const totalProofsEl = document.getElementById('total-proofs');
const thisMonthEl = document.getElementById('this-month');
const recentProofsEl = document.getElementById('recent-proofs');
const statusEl = document.getElementById('status');

// Initialize popup
async function init() {
  try {
    // Check authentication
    const { token } = await chrome.runtime.sendMessage({ action: 'getAuthToken' });
    
    if (token) {
      showMainSection();
      await loadStats();
      await loadRecentProofs();
    } else {
      showAuthSection();
    }
  } catch (error) {
    console.error('Error initializing popup:', error);
    showAuthSection();
  }
}

// Show auth section
function showAuthSection() {
  authSection.style.display = 'block';
  mainSection.style.display = 'none';
}

// Show main section
function showMainSection() {
  authSection.style.display = 'none';
  mainSection.style.display = 'block';
}

// Load user stats
async function loadStats() {
  try {
    const { token } = await chrome.runtime.sendMessage({ action: 'getAuthToken' });
    
    const response = await fetch(`${API_URL}/users/me/stats`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.ok) {
      const stats = await response.json();
      totalProofsEl.textContent = stats.total_proofs || 0;
      thisMonthEl.textContent = stats.this_month || 0;
    }
  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

// Load recent proofs
async function loadRecentProofs() {
  try {
    const { token } = await chrome.runtime.sendMessage({ action: 'getAuthToken' });
    
    const response = await fetch(`${API_URL}/proofs?limit=5`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.ok) {
      const proofs = await response.json();
      displayRecentProofs(proofs);
    }
  } catch (error) {
    console.error('Error loading recent proofs:', error);
  }
}

// Display recent proofs
function displayRecentProofs(proofs) {
  if (!proofs || proofs.length === 0) {
    recentProofsEl.innerHTML = `
      <div class="empty-state">
        <p>No proofs yet</p>
        <p class="empty-hint">Create your first proof above</p>
      </div>
    `;
    return;
  }
  
  recentProofsEl.innerHTML = proofs.map(proof => `
    <div class="recent-item" data-proof-id="${proof.id}">
      <div class="recent-item-title">${proof.title || 'Untitled Proof'}</div>
      <div class="recent-item-meta">
        <span class="recent-item-type">${proof.type}</span>
        <span>${formatDate(proof.created_at)}</span>
      </div>
    </div>
  `).join('');
  
  // Add click handlers
  document.querySelectorAll('.recent-item').forEach(item => {
    item.addEventListener('click', () => {
      const proofId = item.dataset.proofId;
      openProofLink(proofId);
    });
  });
}

// Format date
function formatDate(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  
  return date.toLocaleDateString();
}

// Open proof link
function openProofLink(proofId) {
  chrome.tabs.create({
    url: `https://prooflink.ai/verify/${proofId}`
  });
}

// Event Listeners
loginBtn.addEventListener('click', () => {
  chrome.tabs.create({
    url: 'https://prooflink.ai/auth/login'
  });
});

registerBtn.addEventListener('click', () => {
  chrome.tabs.create({
    url: 'https://prooflink.ai/auth/register'
  });
});

proofPageBtn.addEventListener('click', async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Send message to background script
    chrome.runtime.sendMessage({
      action: 'createProof',
      data: {
        type: 'webpage',
        url: tab.url,
        title: tab.title
      }
    }, (response) => {
      if (response.success) {
        showSuccess('Proof created successfully!');
        loadStats();
        loadRecentProofs();
      } else {
        showError('Failed to create proof');
      }
    });
  } catch (error) {
    console.error('Error creating proof:', error);
    showError('Failed to create proof');
  }
});

proofSelectionBtn.addEventListener('click', async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Get selected text from content script
    const response = await chrome.tabs.sendMessage(tab.id, {
      action: 'captureSelection'
    });
    
    if (response.selection) {
      chrome.runtime.sendMessage({
        action: 'createProof',
        data: {
          type: 'text',
          content: response.selection
        }
      }, (response) => {
        if (response.success) {
          showSuccess('Proof created successfully!');
          loadStats();
          loadRecentProofs();
        } else {
          showError('Failed to create proof');
        }
      });
    } else {
      showError('No text selected');
    }
  } catch (error) {
    console.error('Error creating proof:', error);
    showError('Please select some text first');
  }
});

verifyBtn.addEventListener('click', async () => {
  try {
    const text = await navigator.clipboard.readText();
    
    chrome.runtime.sendMessage({
      action: 'verifyProof',
      proofId: extractProofId(text)
    }, (response) => {
      if (response.success && response.verification.valid) {
        showSuccess('Proof is valid!');
      } else {
        showError('Proof is invalid or not found');
      }
    });
  } catch (error) {
    console.error('Error verifying proof:', error);
    showError('Failed to verify proof');
  }
});

settingsBtn.addEventListener('click', () => {
  chrome.runtime.openOptionsPage();
});

dashboardBtn.addEventListener('click', () => {
  chrome.tabs.create({
    url: 'https://prooflink.ai/dashboard'
  });
});

// Helper functions
function extractProofId(text) {
  const urlMatch = text.match(/prooflink\.ai\/verify\/([a-zA-Z0-9-]+)/);
  if (urlMatch) return urlMatch[1];
  
  const uuidMatch = text.match(/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/i);
  if (uuidMatch) return uuidMatch[0];
  
  return null;
}

function showSuccess(message) {
  const notification = document.createElement('div');
  notification.className = 'notification success';
  notification.textContent = message;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.remove();
  }, 3000);
}

function showError(message) {
  const notification = document.createElement('div');
  notification.className = 'notification error';
  notification.textContent = message;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.remove();
  }, 3000);
}

// Initialize on load
init();