'use client';

import { useState, useEffect } from 'react';
import {
  RefreshCw,
  Copy,
  CheckCircle,
  Zap,
  Shield,
  Lock,
  Eye,
  EyeOff,
} from 'lucide-react';
import Link from 'next/link';

export default function PasswordGeneratorPage() {
  const [password, setPassword] = useState('');
  const [length, setLength] = useState(16);
  const [options, setOptions] = useState({
    uppercase: true,
    lowercase: true,
    numbers: true,
    symbols: true,
  });
  const [copied, setCopied] = useState(false);
  const [showPassword, setShowPassword] = useState(true);
  const [strength, setStrength] = useState(0);

  const generatePassword = () => {
    let charset = '';
    if (options.uppercase) charset += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    if (options.lowercase) charset += 'abcdefghijklmnopqrstuvwxyz';
    if (options.numbers) charset += '0123456789';
    if (options.symbols) charset += '!@#$%^&*()_+-=[]{}|;:,.<>?';

    let newPassword = '';
    for (let i = 0; i < length; i++) {
      newPassword += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    setPassword(newPassword);
    calculateStrength(newPassword);
  };

  const calculateStrength = (pwd: string) => {
    let score = 0;
    if (pwd.length >= 8) score += 25;
    if (pwd.length >= 12) score += 25;
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score += 25;
    if (/\d/.test(pwd)) score += 12.5;
    if (/[^a-zA-Z\d]/.test(pwd)) score += 12.5;
    setStrength(Math.min(score, 100));
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(password);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  useEffect(() => {
    generatePassword();
  }, [length, options]);

  const getStrengthColor = () => {
    if (strength < 25) return 'bg-red-500';
    if (strength < 50) return 'bg-orange-500';
    if (strength < 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStrengthText = () => {
    if (strength < 25) return 'Weak';
    if (strength < 50) return 'Fair';
    if (strength < 75) return 'Good';
    return 'Strong';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black bg-opacity-30 backdrop-blur-lg border-b border-white border-opacity-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="text-blue-400 hover:text-blue-300">
                ← Back
              </Link>
              <h1 className="text-2xl font-bold text-white">Password Generator</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Main Generator Card */}
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-8 border border-white border-opacity-10 shadow-2xl mb-8">
          {/* Generated Password Display */}
          <div className="mb-8">
            <label className="block text-white font-semibold mb-3 flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              Generated Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                readOnly
                className="w-full px-6 py-4 bg-slate-700 border border-gray-600 rounded-xl text-white text-lg font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-24"
              />
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex gap-2">
                <button
                  onClick={() => setShowPassword(!showPassword)}
                  className="p-2 text-gray-400 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
                <button
                  onClick={copyToClipboard}
                  className="p-2 text-gray-400 hover:text-white transition-colors"
                >
                  {copied ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    <Copy className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            {/* Strength Indicator */}
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Password Strength</span>
                <span className={`text-sm font-semibold ${
                  strength < 50 ? 'text-red-400' : 'text-green-400'
                }`}>
                  {getStrengthText()}
                </span>
              </div>
              <div className="w-full h-3 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getStrengthColor()} transition-all duration-300`}
                  style={{ width: `${strength}%` }}
                />
              </div>
            </div>
          </div>

          {/* Length Slider */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-3">
              <label className="text-white font-semibold">Password Length</label>
              <span className="text-blue-400 font-bold text-lg">{length}</span>
            </div>
            <input
              type="range"
              min="8"
              max="64"
              value={length}
              onChange={(e) => setLength(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>8</span>
              <span>64</span>
            </div>
          </div>

          {/* Options */}
          <div className="space-y-4 mb-8">
            <label className="text-white font-semibold block mb-3">Include Characters</label>
            {[
              { key: 'uppercase', label: 'Uppercase (A-Z)', example: 'ABC' },
              { key: 'lowercase', label: 'Lowercase (a-z)', example: 'abc' },
              { key: 'numbers', label: 'Numbers (0-9)', example: '123' },
              { key: 'symbols', label: 'Symbols (!@#$%)', example: '!@#' },
            ].map((option) => (
              <div
                key={option.key}
                className="flex items-center justify-between p-4 bg-slate-700 bg-opacity-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={options[option.key as keyof typeof options]}
                    onChange={(e) =>
                      setOptions({ ...options, [option.key]: e.target.checked })
                    }
                    className="w-5 h-5 text-blue-600 bg-slate-600 border-gray-500 rounded focus:ring-blue-500"
                  />
                  <div>
                    <span className="text-white">{option.label}</span>
                    <span className="text-gray-400 text-sm ml-2 font-mono">{option.example}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={generatePassword}
              className="flex-1 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all font-semibold flex items-center justify-center gap-2"
            >
              <RefreshCw className="w-5 h-5" />
              Generate New Password
            </button>
            <button
              onClick={copyToClipboard}
              className="px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-all font-semibold flex items-center gap-2"
            >
              {copied ? (
                <>
                  <CheckCircle className="w-5 h-5" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-5 h-5" />
                  Copy
                </>
              )}
            </button>
          </div>
        </div>

        {/* Tips */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-blue-900 to-indigo-900 bg-opacity-30 rounded-xl p-6 border border-blue-500 border-opacity-30">
            <Shield className="w-8 h-8 text-blue-400 mb-3" />
            <h3 className="text-white font-bold mb-2">Use Unique Passwords</h3>
            <p className="text-blue-200 text-sm">
              Never reuse passwords across different accounts. Generate a unique password for each service.
            </p>
          </div>

          <div className="bg-gradient-to-br from-purple-900 to-pink-900 bg-opacity-30 rounded-xl p-6 border border-purple-500 border-opacity-30">
            <Lock className="w-8 h-8 text-purple-400 mb-3" />
            <h3 className="text-white font-bold mb-2">Longer is Stronger</h3>
            <p className="text-purple-200 text-sm">
              Passwords with 16+ characters are exponentially harder to crack. Aim for at least 12 characters.
            </p>
          </div>

          <div className="bg-gradient-to-br from-green-900 to-emerald-900 bg-opacity-30 rounded-xl p-6 border border-green-500 border-opacity-30">
            <Zap className="w-8 h-8 text-green-400 mb-3" />
            <h3 className="text-white font-bold mb-2">Mix It Up</h3>
            <p className="text-green-200 text-sm">
              Include uppercase, lowercase, numbers, and symbols for maximum security.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}