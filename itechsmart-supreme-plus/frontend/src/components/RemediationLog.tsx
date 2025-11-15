/**
 * iTechSmart Supreme Plus - Remediation Log Component
 * Displays remediation execution results
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { Terminal, CheckCircle, XCircle } from 'lucide-react';

interface RemediationLogProps {
  result: any;
}

export default function RemediationLog({ result }: RemediationLogProps) {
  return (
    <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
      <div className="flex items-center space-x-2 mb-3">
        <Terminal className="w-4 h-4 text-slate-400" />
        <h4 className="text-sm font-semibold text-slate-300">Execution Result</h4>
        {result.success ? (
          <CheckCircle className="w-4 h-4 text-green-500" />
        ) : (
          <XCircle className="w-4 h-4 text-red-500" />
        )}
      </div>
      
      {result.output && (
        <div className="mb-3">
          <p className="text-xs text-slate-500 mb-1">Output:</p>
          <pre className="text-xs text-slate-300 bg-slate-950 p-2 rounded overflow-x-auto">
            {result.output}
          </pre>
        </div>
      )}
      
      {result.error && (
        <div>
          <p className="text-xs text-red-400 mb-1">Error:</p>
          <pre className="text-xs text-red-300 bg-red-950/20 p-2 rounded overflow-x-auto">
            {result.error}
          </pre>
        </div>
      )}
      
      {result.exit_code !== undefined && (
        <p className="text-xs text-slate-500 mt-2">
          Exit Code: <span className={result.exit_code === 0 ? 'text-green-500' : 'text-red-500'}>
            {result.exit_code}
          </span>
        </p>
      )}
    </div>
  );
}