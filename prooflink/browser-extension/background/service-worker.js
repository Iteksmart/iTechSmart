// ProofLink.AI Browser Extension - Background Service Worker

const API_BASE_URL = 'https://api.prooflink.ai/api/v1';
const LOCAL_API_URL = 'http://localhost:8000/api/v1';

// State management
let authToken = null;
let apiUrl = API_BASE_URL;

// Initialize extension
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('ProofLink.AI extension installed:', details.reason);
  
  // Create context menus
  createContextMenus();
  
  // Load saved settings
  const settings = await chrome.storage.sync.get(['apiUrl', 'authToken']);
  if (settings.apiUrl) apiUrl = settings.apiUrl;
  if (settings.authToken) authToken = settings.authToken;
  
  // Show welcome notification
  if (details.reason === 'install') {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: '../icons/icon128.png',
      title: 'ProofLink.AI Installed',
      message: 'Click the extension icon to get started!'
    });
  }
});

// Create context menus
function createContextMenus() {
  chrome.contextMenus.removeAll(() => {
    // Create proof of page
    chrome.contextMenus.create({
      id: 'create-proof-page',
      title: 'Create Proof of This Page',
      contexts: ['page']
    });
    
    // Create proof of selection
    chrome.contextMenus.create({
      id: 'create-proof-selection',
      title: 'Create Proof of Selection',
      contexts: ['selection']
    });
    
    // Create proof of image
    chrome.contextMenus.create({
      id: 'create-proof-image',
      title: 'Create Proof of This Image',
      contexts: ['image']
    });
    
    // Create proof of link
    chrome.contextMenus.create({
      id: 'create-proof-link',
      title: 'Create Proof of This Link',
      contexts: ['link']
    });
    
    // Verify proof
    chrome.contextMenus.create({
      id: 'verify-proof',
      title: 'Verify Proof from Clipboard',
      contexts: ['page']
    });
  });
}

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  switch (info.menuItemId) {
    case 'create-proof-page':
      await createProofOfPage(tab);
      break;
    case 'create-proof-selection':
      await createProofOfSelection(info.selectionText, tab);
      break;
    case 'create-proof-image':
      await createProofOfImage(info.srcUrl, tab);
      break;
    case 'create-proof-link':
      await createProofOfLink(info.linkUrl, tab);
      break;
    case 'verify-proof':
      await verifyProofFromClipboard(tab);
      break;
  }
});

// Handle keyboard commands
chrome.commands.onCommand.addListener(async (command) => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  switch (command) {
    case 'create-proof':
      await createProofOfPage(tab);
      break;
    case 'verify-proof':
      await verifyProofFromClipboard(tab);
      break;
  }
});

// Handle messages from popup and content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  (async () => {
    try {
      switch (request.action) {
        case 'createProof':
          const proof = await createProof(request.data);
          sendResponse({ success: true, proof });
          break;
        
        case 'verifyProof':
          const verification = await verifyProof(request.proofId);
          sendResponse({ success: true, verification });
          break;
        
        case 'getAuthToken':
          sendResponse({ success: true, token: authToken });
          break;
        
        case 'setAuthToken':
          authToken = request.token;
          await chrome.storage.sync.set({ authToken });
          sendResponse({ success: true });
          break;
        
        case 'logout':
          authToken = null;
          await chrome.storage.sync.remove('authToken');
          sendResponse({ success: true });
          break;
        
        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      console.error('Error handling message:', error);
      sendResponse({ success: false, error: error.message });
    }
  })();
  
  return true; // Keep message channel open for async response
});

// Create proof of current page
async function createProofOfPage(tab) {
  try {
    // Inject content script to capture page content
    const [result] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        return {
          html: document.documentElement.outerHTML,
          url: window.location.href,
          title: document.title
        };
      }
    });
    
    const pageData = result.result;
    
    // Create proof
    const proof = await createProof({
      type: 'webpage',
      content: pageData.html,
      metadata: {
        url: pageData.url,
        title: pageData.title,
        timestamp: new Date().toISOString()
      }
    });
    
    // Show success notification
    showNotification('Proof Created', `Proof of "${pageData.title}" created successfully!`);
    
    // Copy proof link to clipboard
    await copyToClipboard(proof.proof_link);
    
  } catch (error) {
    console.error('Error creating proof:', error);
    showNotification('Error', 'Failed to create proof. Please try again.');
  }
}

// Create proof of selected text
async function createProofOfSelection(text, tab) {
  try {
    const proof = await createProof({
      type: 'text',
      content: text,
      metadata: {
        source: tab.url,
        timestamp: new Date().toISOString()
      }
    });
    
    showNotification('Proof Created', 'Proof of selected text created!');
    await copyToClipboard(proof.proof_link);
    
  } catch (error) {
    console.error('Error creating proof:', error);
    showNotification('Error', 'Failed to create proof.');
  }
}

// Create proof of image
async function createProofOfImage(imageUrl, tab) {
  try {
    // Download image as blob
    const response = await fetch(imageUrl);
    const blob = await response.blob();
    
    // Convert to base64
    const base64 = await blobToBase64(blob);
    
    const proof = await createProof({
      type: 'image',
      content: base64,
      metadata: {
        source: imageUrl,
        page: tab.url,
        timestamp: new Date().toISOString()
      }
    });
    
    showNotification('Proof Created', 'Proof of image created!');
    await copyToClipboard(proof.proof_link);
    
  } catch (error) {
    console.error('Error creating proof:', error);
    showNotification('Error', 'Failed to create proof of image.');
  }
}

// Create proof of link
async function createProofOfLink(linkUrl, tab) {
  try {
    const proof = await createProof({
      type: 'link',
      content: linkUrl,
      metadata: {
        source: tab.url,
        timestamp: new Date().toISOString()
      }
    });
    
    showNotification('Proof Created', 'Proof of link created!');
    await copyToClipboard(proof.proof_link);
    
  } catch (error) {
    console.error('Error creating proof:', error);
    showNotification('Error', 'Failed to create proof.');
  }
}

// Verify proof from clipboard
async function verifyProofFromClipboard(tab) {
  try {
    // Read from clipboard
    const text = await navigator.clipboard.readText();
    
    // Extract proof ID from URL or text
    const proofId = extractProofId(text);
    
    if (!proofId) {
      showNotification('Error', 'No valid proof link found in clipboard.');
      return;
    }
    
    // Verify proof
    const verification = await verifyProof(proofId);
    
    if (verification.valid) {
      showNotification('Proof Valid ✓', `Verified on ${new Date(verification.timestamp).toLocaleString()}`);
    } else {
      showNotification('Proof Invalid ✗', 'This proof could not be verified.');
    }
    
  } catch (error) {
    console.error('Error verifying proof:', error);
    showNotification('Error', 'Failed to verify proof.');
  }
}

// API Functions
async function createProof(data) {
  const response = await fetch(`${apiUrl}/proofs`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error('Failed to create proof');
  }
  
  return await response.json();
}

async function verifyProof(proofId) {
  const response = await fetch(`${apiUrl}/proofs/${proofId}/verify`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to verify proof');
  }
  
  return await response.json();
}

// Helper Functions
function extractProofId(text) {
  // Try to extract from URL
  const urlMatch = text.match(/prooflink\.ai\/verify\/([a-zA-Z0-9-]+)/);
  if (urlMatch) return urlMatch[1];
  
  // Try to extract UUID
  const uuidMatch = text.match(/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/i);
  if (uuidMatch) return uuidMatch[0];
  
  return null;
}

async function copyToClipboard(text) {
  await navigator.clipboard.writeText(text);
}

function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

function showNotification(title, message) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: '../icons/icon128.png',
    title,
    message
  });
}

// Keep service worker alive
chrome.runtime.onStartup.addListener(() => {
  console.log('ProofLink.AI extension started');
});