/**
 * iTechSmart Supreme Plus - Incident Card Component
 * Displays individual incident information
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { Brain } from 'lucide-react';

interface IncidentCardProps {
  incident: any;
  onAnalyze: (id: number) => void;
  getSeverityColor: (severity: string) => string;
  getStatusIcon: (status: string) => JSX.Element;
}

export default function IncidentCard({ 
  incident, 
  onAnalyze, 
  getSeverityColor, 
  getStatusIcon 
}: IncidentCardProps) {
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            {getStatusIcon(incident.status)}
            <h3 className="text-lg font-semibold text-white">{incident.title}</h3>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getSeverityColor(incident.severity)}`}>
              {incident.severity}
            </span>
          </div>
          <p className="text-slate-400 mb-4">{incident.description}</p>
          <div className="flex items-center space-x-4 text-sm text-slate-500">
            <span>Source: {incident.source}</span>
            <span>•</span>
            <span>Created: {new Date(incident.created_at).toLocaleString()}</span>
            {incident.resolved_at && (
              <>
                <span>•</span>
                <span>Resolved: {new Date(incident.resolved_at).toLocaleString()}</span>
              </>
            )}
          </div>
        </div>
        {incident.status === 'open' && (
          <button
            onClick={() => onAnalyze(incident.id)}
            className="ml-4 bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center"
          >
            <Brain className="w-4 h-4 mr-2" />
            AI Analyze
          </button>
        )}
      </div>
    </div>
  );
}