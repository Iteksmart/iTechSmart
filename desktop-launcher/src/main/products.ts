export interface Product {
  id: string;
  name: string;
  description: string;
  category: string;
  backendPort: number;
  frontendPort: number;
  icon: string;
  tier: 'trial' | 'starter' | 'professional' | 'enterprise' | 'unlimited';
}

export const PRODUCTS: Product[] = [
  // Core Infrastructure (8 products)
  {
    id: 'itechsmart-enterprise',
    name: 'iTechSmart Enterprise',
    description: 'Enterprise management platform',
    category: 'Core Infrastructure',
    backendPort: 8001,
    frontendPort: 3001,
    icon: 'enterprise.png',
    tier: 'trial'
  },
  {
    id: 'itechsmart-ninja',
    name: 'iTechSmart Ninja',
    description: 'Autonomous IT issue resolution',
    category: 'Core Infrastructure',
    backendPort: 8002,
    frontendPort: 3002,
    icon: 'ninja.png',
    tier: 'trial'
  },
  {
    id: 'itechsmart-supreme-plus',
    name: 'iTechSmart Supreme Plus',
    description: 'Advanced IT automation',
    category: 'Core Infrastructure',
    backendPort: 8003,
    frontendPort: 3003,
    icon: 'supreme.png',
    tier: 'professional'
  },
  {
    id: 'itechsmart-citadel',
    name: 'iTechSmart Citadel',
    description: 'Security operations center',
    category: 'Core Infrastructure',
    backendPort: 8004,
    frontendPort: 3004,
    icon: 'citadel.png',
    tier: 'enterprise'
  },
  {
    id: 'itechsmart-cloud',
    name: 'iTechSmart Cloud',
    description: 'Cloud infrastructure management',
    category: 'Core Infrastructure',
    backendPort: 8005,
    frontendPort: 3005,
    icon: 'cloud.png',
    tier: 'professional'
  },
  {
    id: 'itechsmart-devops',
    name: 'iTechSmart DevOps',
    description: 'DevOps automation',
    category: 'Core Infrastructure',
    backendPort: 8006,
    frontendPort: 3006,
    icon: 'devops.png',
    tier: 'professional'
  },
  {
    id: 'itechsmart-data-platform',
    name: 'iTechSmart Data Platform',
    description: 'Data management',
    category: 'Core Infrastructure',
    backendPort: 8007,
    frontendPort: 3007,
    icon: 'data.png',
    tier: 'enterprise'
  },
  {
    id: 'itechsmart-analytics',
    name: 'iTechSmart Analytics',
    description: 'Business analytics',
    category: 'Core Infrastructure',
    backendPort: 8008,
    frontendPort: 3008,
    icon: 'analytics.png',
    tier: 'trial'
  },

  // Healthcare & Compliance (3 products)
  {
    id: 'itechsmart-hl7',
    name: 'iTechSmart HL7',
    description: 'Healthcare data integration',
    category: 'Healthcare & Compliance',
    backendPort: 8009,
    frontendPort: 3009,
    icon: 'hl7.png',
    tier: 'enterprise'
  },
  {
    id: 'itechsmart-impactos',
    name: 'iTechSmart Impactos',
    description: 'Healthcare impact analysis',
    category: 'Healthcare & Compliance',
    backendPort: 8010,
    frontendPort: 3010,
    icon: 'impactos.png',
    tier: 'enterprise'
  },
  {
    id: 'itechsmart-compliance',
    name: 'iTechSmart Compliance',
    description: 'Regulatory compliance',
    category: 'Healthcare & Compliance',
    backendPort: 8011,
    frontendPort: 3011,
    icon: 'compliance.png',
    tier: 'professional'
  },

  // Development & Operations (8 products)
  {
    id: 'itechsmart-forge',
    name: 'iTechSmart Forge',
    description: 'Development platform',
    category: 'Development & Operations',
    backendPort: 8012,
    frontendPort: 3012,
    icon: 'forge.png',
    tier: 'professional'
  },
  {
    id: 'itechsmart-copilot',
    name: 'iTechSmart Copilot',
    description: 'AI coding assistant',
    category: 'Development & Operations',
    backendPort: 8013,
    frontendPort: 3013,
    icon: 'copilot.png',
    tier: 'professional'
  },
  {
    id: 'itechsmart-workflow',
    name: 'iTechSmart Workflow',
    description: 'Workflow automation',
    category: 'Development & Operations',
    backendPort: 8014,
    frontendPort: 3014,
    icon: 'workflow.png',
    tier: 'starter'
  },
  {
    id: 'itechsmart-qaqc',
    name: 'iTechSmart QA/QC',
    description: 'Quality assurance',
    category: 'Development & Operations',
    backendPort: 8015,
    frontendPort: 3015,
    icon: 'qaqc.png',
    tier: 'professional'
  },
  {
    id: 'itechsmart-sandbox',
    name: 'iTechSmart Sandbox',
    description: 'Testing environment',
    category: 'Development & Operations',
    backendPort: 8016,
    frontendPort: 3016,
    icon: 'sandbox.png',
    tier: 'professional'
  },
  {
    id: 'itechsmart-observatory',
    name: 'iTechSmart Observatory',
    description: 'System monitoring',
    category: 'Development & Operations',
    backendPort: 8017,
    frontendPort: 3017,
    icon: 'observatory.png',
    tier: 'starter'
  },
  {
    id: 'itechsmart-pulse',
    name: 'iTechSmart Pulse',
    description: 'Performance monitoring',
    category: 'Development & Operations',
    backendPort: 8018,
    frontendPort: 3018,
    icon: 'pulse.png',
    tier: 'starter'
  },
  {
    id: 'itechsmart-port-manager',
    name: 'iTechSmart Port Manager',
    description: 'Port management',
    category: 'Development & Operations',
    backendPort: 8019,
    frontendPort: 3019,
    icon: 'port.png',
    tier: 'starter'
  },

  // Security & Governance (6 products)
  {
    id: 'itechsmart-shield',
    name: 'iTechSmart Shield',
    description: 'Security management',
    category: 'Security & Governance',
    backendPort: 8020,
    frontendPort: 3020,
    icon: 'shield.png',
    tier: 'enterprise'
  },
  {
    id: 'itechsmart-sentinel',
    name: 'iTechSmart Sentinel',
    description: 'Threat detection',
    category: 'Security & Governance',
    backendPort: 8021,
    frontendPort: 3021,
    icon: 'sentinel.png',
    tier: 'enterprise'
  },
  {
    id: 'itechsmart-vault',
    name: 'iTechSmart Vault',
    description: 'Secrets management',
    category: 'Security & Governance',
    backendPort: 8022,
    frontendPort: 3022,
    icon: 'vault.png',
    tier: 'professional'
  },
  {
    id: 'itechsmart-ledger',
    name: 'iTechSmart Ledger',
    description: 'Blockchain ledger',
    category: 'Security & Governance',
    backendPort: 8023,
    frontendPort: 3023,
    icon: 'ledger.png',
    tier: 'enterprise'
  },
  {
    id: 'legalai-pro',
    name: 'LegalAI Pro',
    description: 'Legal AI assistant',
    category: 'Security & Governance',
    backendPort: 8024,
    frontendPort: 3024,
    icon: 'legal.png',
    tier: 'professional'
  },
  {
    id: 'passport',
    name: 'Passport',
    description: 'Identity management',
    category: 'Security & Governance',
    backendPort: 8025,
    frontendPort: 3025,
    icon: 'passport.png',
    tier: 'professional'
  },

  // Business & Integration (8 products)
  {
    id: 'itechsmart-marketplace',
    name: 'iTechSmart Marketplace',
    description: 'App marketplace',
    category: 'Business & Integration',
    backendPort: 8026,
    frontendPort: 3026,
    icon: 'marketplace.png',
    tier: 'starter'
  },
  {
    id: 'itechsmart-connect',
    name: 'iTechSmart Connect',
    description: 'Integration platform',
    category: 'Business & Integration',
    backendPort: 8027,
    frontendPort: 3027,
    icon: 'connect.png',
    tier: 'professional'
  },
  {
    id: 'itechsmart-notify',
    name: 'iTechSmart Notify',
    description: 'Notification system',
    category: 'Business & Integration',
    backendPort: 8028,
    frontendPort: 3028,
    icon: 'notify.png',
    tier: 'starter'
  },
  {
    id: 'itechsmart-customer-success',
    name: 'iTechSmart Customer Success',
    description: 'Customer management',
    category: 'Business & Integration',
    backendPort: 8029,
    frontendPort: 3029,
    icon: 'customer.png',
    tier: 'professional'
  },
  {
    id: 'itechsmart-mobile',
    name: 'iTechSmart Mobile',
    description: 'Mobile management',
    category: 'Business & Integration',
    backendPort: 8030,
    frontendPort: 3030,
    icon: 'mobile.png',
    tier: 'professional'
  },
  {
    id: 'itechsmart-ai',
    name: 'iTechSmart AI',
    description: 'AI services',
    category: 'Business & Integration',
    backendPort: 8031,
    frontendPort: 3031,
    icon: 'ai.png',
    tier: 'professional'
  },
  {
    id: 'itechsmart-dataflow',
    name: 'iTechSmart DataFlow',
    description: 'Data pipeline',
    category: 'Business & Integration',
    backendPort: 8032,
    frontendPort: 3032,
    icon: 'dataflow.png',
    tier: 'enterprise'
  },
  {
    id: 'itechsmart-mdm-agent',
    name: 'iTechSmart MDM Agent',
    description: 'Mobile device management',
    category: 'Business & Integration',
    backendPort: 8033,
    frontendPort: 3033,
    icon: 'mdm.png',
    tier: 'professional'
  },

  // Specialized Tools (2 products)
  {
    id: 'itechsmart-thinktank',
    name: 'iTechSmart ThinkTank',
    description: 'Collaboration platform',
    category: 'Specialized Tools',
    backendPort: 8034,
    frontendPort: 3034,
    icon: 'thinktank.png',
    tier: 'starter'
  },
  {
    id: 'prooflink',
    name: 'ProofLink',
    description: 'Document verification',
    category: 'Specialized Tools',
    backendPort: 8035,
    frontendPort: 3035,
    icon: 'prooflink.png',
    tier: 'professional'
  }
];

export function getProductsByCategory(): Record<string, Product[]> {
  const categories: Record<string, Product[]> = {};
  
  PRODUCTS.forEach(product => {
    if (!categories[product.category]) {
      categories[product.category] = [];
    }
    categories[product.category].push(product);
  });

  return categories;
}

export function getProductsByTier(tier: string): Product[] {
  if (tier === 'unlimited' || tier === 'enterprise') {
    return PRODUCTS;
  }

  return PRODUCTS.filter(p => {
    const tierOrder = ['trial', 'starter', 'professional', 'enterprise', 'unlimited'];
    const productTierIndex = tierOrder.indexOf(p.tier);
    const userTierIndex = tierOrder.indexOf(tier);
    return productTierIndex <= userTierIndex;
  });
}