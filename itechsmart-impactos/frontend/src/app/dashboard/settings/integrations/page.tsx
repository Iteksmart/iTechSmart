'use client';

import Link from 'next/link';
import { ArrowLeft, CheckCircle, XCircle } from 'lucide-react';

export default function IntegrationsSettingsPage() {
  const integrations = [
    { name: 'Google Analytics', description: 'Track website analytics', connected: true },
    { name: 'Mailchimp', description: 'Email marketing automation', connected: false },
    { name: 'Slack', description: 'Team communication', connected: true },
    { name: 'Stripe', description: 'Payment processing', connected: false }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/dashboard/settings" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Integrations</h1>
          <p className="mt-1 text-sm text-gray-500">Connect third-party services</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {integrations.map((integration, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{integration.name}</h3>
                <p className="text-sm text-gray-500 mt-1">{integration.description}</p>
              </div>
              {integration.connected ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : (
                <XCircle className="w-6 h-6 text-gray-400" />
              )}
            </div>
            <button
              className={`w-full px-4 py-2 rounded-lg transition-colors ${
                integration.connected
                  ? 'bg-red-600 text-white hover:bg-red-700'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {integration.connected ? 'Disconnect' : 'Connect'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}