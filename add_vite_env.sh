#!/bin/bash

# Add vite-env.d.ts to all Vite projects

VITE_PROJECTS=(
  "itechsmart-ai"
  "itechsmart-citadel"
  "itechsmart-connect"
  "itechsmart-copilot"
  "itechsmart-dataflow"
  "itechsmart-enterprise"
  "itechsmart-forge"
  "itechsmart-hl7"
  "itechsmart-ledger"
  "itechsmart-marketplace"
  "itechsmart-mdm-agent"
  "itechsmart-notify"
  "itechsmart-port-manager"
  "itechsmart-qaqc"
  "itechsmart-sandbox"
  "itechsmart-sentinel"
  "itechsmart-shield"
  "itechsmart-supreme-plus"
  "itechsmart-thinktank"
  "itechsmart-vault"
)

for project in "${VITE_PROJECTS[@]}"; do
  if [ ! -f "$project/frontend/src/vite-env.d.ts" ]; then
    cat > "$project/frontend/src/vite-env.d.ts" << 'EOF'
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_APP_TITLE?: string
  // Add other env variables as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
EOF
    echo "✅ Created vite-env.d.ts for $project"
  else
    echo "⏭️  Skipped $project (already exists)"
  fi
done

echo ""
echo "✅ Complete! Added vite-env.d.ts to all Vite projects"