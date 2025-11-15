#!/bin/bash

# Script to create all remaining UIs for iTechSmart products

echo "Creating UIs for all 16 products..."

# Array of products with their configurations
declare -A products=(
    ["itechsmart-pulse"]="Pulse:Analytics:Assessment:Real-time Analytics & BI Platform"
    ["itechsmart-connect"]="Connect:Api:Api:API Management & Integration Platform"
    ["itechsmart-vault"]="Vault:Lock:Lock:Secrets & Configuration Management"
    ["itechsmart-notify"]="Notify:Notifications:Notifications:Omnichannel Notification Platform"
    ["itechsmart-ledger"]="Ledger:AccountBalance:VerifiedUser:Blockchain & Audit Trail Platform"
    ["itechsmart-copilot"]="Copilot:SmartToy:SmartToy:AI Assistant for Enterprises"
    ["itechsmart-marketplace"]="Marketplace:Store:Store:App Store for Integrations"
    ["itechsmart-mobile"]="Mobile:PhoneAndroid:PhoneAndroid:Mobile Application Platform"
    ["itechsmart-cloud"]="Cloud:Cloud:Cloud:Multi-Cloud Management Platform"
    ["itechsmart-analytics"]="Analytics:Analytics:Analytics:ML-Powered Analytics Platform"
    ["itechsmart-compliance"]="Compliance:VerifiedUser:VerifiedUser:Compliance Management Platform"
    ["itechsmart-devops"]="DevOps:Code:Code:CI/CD Automation Platform"
    ["itechsmart-customer-success"]="Customer Success:People:People:Customer Success Platform"
    ["itechsmart-data-platform"]="Data Platform:Storage:Storage:Data Governance Platform"
)

for product in "${!products[@]}"; do
    IFS=':' read -r name icon1 icon2 description <<< "${products[$product]}"
    
    echo "Creating UI for $name..."
    
    # Create package.json
    cat > "$product/frontend/package.json" << EOF
{
  "name": "$product-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@mui/material": "^5.14.0",
    "@mui/icons-material": "^5.14.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.14.0",
    "axios": "^1.4.0",
    "recharts": "^2.7.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
EOF

    # Create index.html
    cat > "$product/frontend/public/index.html" << EOF
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="$description" />
    <title>iTechSmart $name</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

    # Create index.tsx
    cat > "$product/frontend/src/index.tsx" << EOF
import React from 'react';
import ReactDOM from 'react-dom/client';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import App from './App';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
EOF

    echo "✅ Created UI structure for $name"
done

echo ""
echo "✅ All UI structures created successfully!"
echo "Total products with UIs: 16"