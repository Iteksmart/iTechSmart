/**
 * iTechSmart Citadel - Security Status Component
 * Displays current security posture
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { Shield, Lock, Eye, Database } from 'lucide-react';

export default function SecurityStatus() {
  const securityControls = [
    { name: 'Firewall', status: 'active', icon: Shield, color: 'text-green-500' },
    { name: 'IDS/IPS', status: 'active', icon: Eye, color: 'text-green-500' },
    { name: 'Encryption', status: 'active', icon: Lock, color: 'text-green-500' },
    { name: 'Backup', status: 'active', icon: Database, color: 'text-green-500' },
  ];

  return (
    <div className="space-y-4">
      {securityControls.map((control) => {
        const Icon = control.icon;
        return (
          <div key={control.name} className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Icon className={`w-5 h-5 ${control.color}`} />
              <span className="text-white font-medium">{control.name}</span>
            </div>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-900/20 text-green-500">
              {control.status}
            </span>
          </div>
        );
      })}
    </div>
  );
}