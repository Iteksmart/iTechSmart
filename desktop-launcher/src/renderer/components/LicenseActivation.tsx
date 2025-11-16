import React, { useState } from 'react';
import { Key, CheckCircle, XCircle, Loader } from 'lucide-react';

interface LicenseActivationProps {
  currentLicense: any;
  onLicenseActivated: (license: any) => void;
}

function LicenseActivation({ currentLicense, onLicenseActivated }: LicenseActivationProps) {
  const [licenseKey, setLicenseKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleActivate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!licenseKey.trim()) {
      setMessage({ type: 'error', text: 'Please enter a license key' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const result = await window.electron.activateLicense(licenseKey);
      
      if (result.success) {
        setMessage({ type: 'success', text: result.message });
        const newLicense = await window.electron.getLicense();
        onLicenseActivated(newLicense);
        setLicenseKey('');
      } else {
        setMessage({ type: 'error', text: result.message });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to activate license. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const formatLicenseKey = (value: string) => {
    // Remove non-alphanumeric characters
    const cleaned = value.replace(/[^A-Z0-9]/gi, '').toUpperCase();
    
    // Split into groups of 4
    const groups = cleaned.match(/.{1,4}/g) || [];
    
    // Join with dashes
    return groups.join('-').substring(0, 24); // XXXX-XXXX-XXXX-XXXX-XXXX
  };

  const handleKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatLicenseKey(e.target.value);
    setLicenseKey(formatted);
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center space-x-3 mb-2">
            <Key size={24} className="text-blue-400" />
            <h2 className="text-2xl font-bold text-slate-100">License Activation</h2>
          </div>
          <p className="text-slate-400">
            Enter your license key to unlock all features of iTechSmart Suite
          </p>
        </div>

        {/* Current License */}
        {currentLicense && (
          <div className="p-6 bg-slate-750 border-b border-slate-700">
            <h3 className="text-sm font-medium text-slate-400 mb-3">Current License</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-slate-500 mb-1">Tier</div>
                <div className="text-lg font-semibold text-blue-400">
                  {currentLicense.tier.toUpperCase()}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Status</div>
                <div className="text-lg font-semibold text-green-400">
                  {currentLicense.isTrial ? 'Trial' : 'Active'}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Max Users</div>
                <div className="text-lg font-semibold text-slate-200">
                  {currentLicense.maxUsers}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Products</div>
                <div className="text-lg font-semibold text-slate-200">
                  {currentLicense.products?.length || 0}
                </div>
              </div>
            </div>
            
            {currentLicense.isTrial && currentLicense.trialEndsAt && (
              <div className="mt-4 p-3 bg-yellow-900/20 border border-yellow-700/30 rounded-lg">
                <p className="text-sm text-yellow-400">
                  Trial expires in {getDaysRemaining(currentLicense.trialEndsAt)} days
                </p>
              </div>
            )}
          </div>
        )}

        {/* Activation Form */}
        <div className="p-6">
          <form onSubmit={handleActivate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                License Key
              </label>
              <input
                type="text"
                value={licenseKey}
                onChange={handleKeyChange}
                placeholder="XXXX-XXXX-XXXX-XXXX-XXXX"
                className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors font-mono text-lg tracking-wider"
                disabled={loading}
              />
              <p className="mt-2 text-xs text-slate-500">
                Enter your 20-character license key (format: XXXX-XXXX-XXXX-XXXX-XXXX)
              </p>
            </div>

            {message && (
              <div className={`p-4 rounded-lg flex items-start space-x-3 ${
                message.type === 'success'
                  ? 'bg-green-900/20 border border-green-700/30'
                  : 'bg-red-900/20 border border-red-700/30'
              }`}>
                {message.type === 'success' ? (
                  <CheckCircle size={20} className="text-green-400 flex-shrink-0 mt-0.5" />
                ) : (
                  <XCircle size={20} className="text-red-400 flex-shrink-0 mt-0.5" />
                )}
                <p className={`text-sm ${
                  message.type === 'success' ? 'text-green-400' : 'text-red-400'
                }`}>
                  {message.text}
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !licenseKey.trim()}
              className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {loading ? (
                <>
                  <Loader size={20} className="animate-spin" />
                  <span>Activating...</span>
                </>
              ) : (
                <>
                  <Key size={20} />
                  <span>Activate License</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Pricing Tiers */}
        <div className="p-6 bg-slate-750 border-t border-slate-700">
          <h3 className="text-sm font-medium text-slate-400 mb-4">Available License Tiers</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <PricingTier
              name="Starter"
              price="$99/mo"
              features={['25 users', '5 products', '10K API calls/day']}
            />
            <PricingTier
              name="Professional"
              price="$499/mo"
              features={['100 users', '15 products', '50K API calls/day']}
            />
            <PricingTier
              name="Enterprise"
              price="$2,499/mo"
              features={['1,000 users', 'All 35 products', '1M API calls/day']}
            />
            <PricingTier
              name="Unlimited"
              price="$9,999/mo"
              features={['Unlimited users', 'All products', 'White-label']}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function PricingTier({ name, price, features }: { name: string; price: string; features: string[] }) {
  return (
    <div className="p-4 bg-slate-800 border border-slate-700 rounded-lg">
      <div className="flex items-baseline justify-between mb-2">
        <h4 className="font-semibold text-slate-200">{name}</h4>
        <span className="text-lg font-bold text-blue-400">{price}</span>
      </div>
      <ul className="space-y-1">
        {features.map((feature, index) => (
          <li key={index} className="text-sm text-slate-400">• {feature}</li>
        ))}
      </ul>
    </div>
  );
}

function getDaysRemaining(expiresAt: string): number {
  const now = new Date();
  const expires = new Date(expiresAt);
  const diff = expires.getTime() - now.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

export default LicenseActivation;