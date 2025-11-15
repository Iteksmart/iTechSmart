// ProofLink.AI Browser Extension - Content Script

console.log('ProofLink.AI content script loaded');

// Inject overlay for proof creation
let overlay = null;

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'showOverlay':
      showOverlay(request.data);
      sendResponse({ success: true });
      break;
    
    case 'hideOverlay':
      hideOverlay();
      sendResponse({ success: true });
      break;
    
    case 'captureSelection':
      const selection = window.getSelection().toString();
      sendResponse({ success: true, selection });
      break;
    
    case 'capturePageData':
      const pageData = {
        html: document.documentElement.outerHTML,
        url: window.location.href,
        title: document.title,
        meta: getPageMetadata()
      };
      sendResponse({ success: true, data: pageData });
      break;
  }
  
  return true;
});

// Show overlay for proof creation
function showOverlay(data) {
  if (overlay) {
    hideOverlay();
  }
  
  overlay = document.createElement('div');
  overlay.id = 'prooflink-overlay';
  overlay.innerHTML = `
    <div class="prooflink-modal">
      <div class="prooflink-header">
        <h2>Creating Proof...</h2>
        <button class="prooflink-close">&times;</button>
      </div>
      <div class="prooflink-content">
        <div class="prooflink-spinner"></div>
        <p>Generating cryptographic proof...</p>
      </div>
    </div>
  `;
  
  document.body.appendChild(overlay);
  
  // Add close handler
  overlay.querySelector('.prooflink-close').addEventListener('click', hideOverlay);
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      hideOverlay();
    }
  });
}

// Hide overlay
function hideOverlay() {
  if (overlay) {
    overlay.remove();
    overlay = null;
  }
}

// Update overlay with success message
function showSuccess(proofLink) {
  if (!overlay) return;
  
  const content = overlay.querySelector('.prooflink-content');
  content.innerHTML = `
    <div class="prooflink-success">
      <div class="prooflink-checkmark">✓</div>
      <h3>Proof Created Successfully!</h3>
      <div class="prooflink-link-container">
        <input type="text" value="${proofLink}" readonly class="prooflink-link-input">
        <button class="prooflink-copy-btn">Copy Link</button>
      </div>
      <p class="prooflink-hint">Link copied to clipboard!</p>
    </div>
  `;
  
  // Add copy handler
  const copyBtn = content.querySelector('.prooflink-copy-btn');
  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(proofLink);
    copyBtn.textContent = 'Copied!';
    setTimeout(() => {
      copyBtn.textContent = 'Copy Link';
    }, 2000);
  });
  
  // Auto-close after 5 seconds
  setTimeout(hideOverlay, 5000);
}

// Update overlay with error message
function showError(message) {
  if (!overlay) return;
  
  const content = overlay.querySelector('.prooflink-content');
  content.innerHTML = `
    <div class="prooflink-error">
      <div class="prooflink-error-icon">✗</div>
      <h3>Error Creating Proof</h3>
      <p>${message}</p>
      <button class="prooflink-retry-btn">Try Again</button>
    </div>
  `;
  
  // Add retry handler
  const retryBtn = content.querySelector('.prooflink-retry-btn');
  retryBtn.addEventListener('click', hideOverlay);
}

// Get page metadata
function getPageMetadata() {
  const metadata = {};
  
  // Get meta tags
  const metaTags = document.querySelectorAll('meta');
  metaTags.forEach(tag => {
    const name = tag.getAttribute('name') || tag.getAttribute('property');
    const content = tag.getAttribute('content');
    if (name && content) {
      metadata[name] = content;
    }
  });
  
  // Get Open Graph data
  const ogTags = document.querySelectorAll('meta[property^="og:"]');
  ogTags.forEach(tag => {
    const property = tag.getAttribute('property');
    const content = tag.getAttribute('content');
    if (property && content) {
      metadata[property] = content;
    }
  });
  
  // Get Twitter Card data
  const twitterTags = document.querySelectorAll('meta[name^="twitter:"]');
  twitterTags.forEach(tag => {
    const name = tag.getAttribute('name');
    const content = tag.getAttribute('content');
    if (name && content) {
      metadata[name] = content;
    }
  });
  
  return metadata;
}

// Add visual indicator when proof is being created
function addProofIndicator(element) {
  element.classList.add('prooflink-creating');
  
  const indicator = document.createElement('div');
  indicator.className = 'prooflink-indicator';
  indicator.innerHTML = '🔒 Creating proof...';
  element.appendChild(indicator);
  
  return indicator;
}

// Remove visual indicator
function removeProofIndicator(indicator) {
  if (indicator) {
    indicator.remove();
  }
}

// Highlight element being proofed
function highlightElement(element) {
  element.classList.add('prooflink-highlighted');
  
  setTimeout(() => {
    element.classList.remove('prooflink-highlighted');
  }, 2000);
}

// Listen for keyboard shortcuts
document.addEventListener('keydown', (e) => {
  // Ctrl/Cmd + Shift + P: Create proof of page
  if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'P') {
    e.preventDefault();
    chrome.runtime.sendMessage({ action: 'createProofOfPage' });
  }
  
  // Ctrl/Cmd + Shift + V: Verify proof
  if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'V') {
    e.preventDefault();
    chrome.runtime.sendMessage({ action: 'verifyProof' });
  }
});

// Add right-click context menu support
document.addEventListener('contextmenu', (e) => {
  // Store clicked element for context menu actions
  window.proofLinkClickedElement = e.target;
});

// Export functions for background script
window.proofLinkContentScript = {
  showOverlay,
  hideOverlay,
  showSuccess,
  showError,
  getPageMetadata,
  addProofIndicator,
  removeProofIndicator,
  highlightElement
};