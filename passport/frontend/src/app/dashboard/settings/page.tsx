"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  User,
  Mail,
  Lock,
  Shield,
  Bell,
  CreditCard,
  Users,
  Download,
  Upload,
  Trash2,
  Check,
  X,
  Eye,
  EyeOff,
  Smartphone,
  Key,
  AlertTriangle,
} from "lucide-react";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("profile");
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [biometricEnabled, setBiometricEnabled] = useState(true);

  const tabs = [
    { id: "profile", label: "Profile", icon: User },
    { id: "security", label: "Security", icon: Shield },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "billing", label: "Billing", icon: CreditCard },
    { id: "family", label: "Family", icon: Users },
    { id: "data", label: "Data", icon: Download },
    { id: "danger", label: "Danger Zone", icon: AlertTriangle },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">Manage your account and preferences</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 p-4">
              <nav className="space-y-2">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                        activeTab === tab.id
                          ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white"
                          : "text-gray-400 hover:bg-white/5"
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="font-medium">{tab.label}</span>
                    </button>
                  );
                })}
              </nav>
            </div>
          </div>

          {/* Content */}
          <div className="lg:col-span-3">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 p-6">
              {/* Profile Tab */}
              {activeTab === "profile" && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">
                    Profile Settings
                  </h2>

                  {/* Avatar */}
                  <div className="mb-6">
                    <label className="block text-gray-400 mb-2">
                      Profile Picture
                    </label>
                    <div className="flex items-center gap-4">
                      <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                        JD
                      </div>
                      <div>
                        <button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors mb-2">
                          Upload New
                        </button>
                        <p className="text-gray-400 text-sm">
                          JPG, PNG or GIF. Max 2MB.
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Full Name */}
                  <div className="mb-6">
                    <label className="block text-gray-400 mb-2">Full Name</label>
                    <input
                      type="text"
                      defaultValue="John Doe"
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    />
                  </div>

                  {/* Email */}
                  <div className="mb-6">
                    <label className="block text-gray-400 mb-2">Email</label>
                    <input
                      type="email"
                      defaultValue="john.doe@example.com"
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    />
                    <p className="text-gray-400 text-sm mt-2">
                      <Check className="w-4 h-4 inline text-green-400" /> Email
                      verified
                    </p>
                  </div>

                  {/* Emergency Contact */}
                  <div className="mb-6">
                    <label className="block text-gray-400 mb-2">
                      Emergency Contact Email
                    </label>
                    <input
                      type="email"
                      placeholder="emergency@example.com"
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                    />
                    <p className="text-gray-400 text-sm mt-2">
                      This person can request emergency access to your vault
                    </p>
                  </div>

                  {/* Save Button */}
                  <button className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all">
                    Save Changes
                  </button>
                </motion.div>
              )}

              {/* Security Tab */}
              {activeTab === "security" && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">
                    Security Settings
                  </h2>

                  {/* Change Password */}
                  <div className="mb-8 p-6 bg-white/5 rounded-lg border border-white/10">
                    <h3 className="text-lg font-semibold text-white mb-4">
                      Change Password
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-gray-400 mb-2">
                          Current Password
                        </label>
                        <div className="relative">
                          <input
                            type={showCurrentPassword ? "text" : "password"}
                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-blue-500"
                          />
                          <button
                            onClick={() =>
                              setShowCurrentPassword(!showCurrentPassword)
                            }
                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                          >
                            {showCurrentPassword ? (
                              <EyeOff className="w-5 h-5" />
                            ) : (
                              <Eye className="w-5 h-5" />
                            )}
                          </button>
                        </div>
                      </div>
                      <div>
                        <label className="block text-gray-400 mb-2">
                          New Password
                        </label>
                        <div className="relative">
                          <input
                            type={showNewPassword ? "text" : "password"}
                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-blue-500"
                          />
                          <button
                            onClick={() => setShowNewPassword(!showNewPassword)}
                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                          >
                            {showNewPassword ? (
                              <EyeOff className="w-5 h-5" />
                            ) : (
                              <Eye className="w-5 h-5" />
                            )}
                          </button>
                        </div>
                      </div>
                      <button className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                        Update Password
                      </button>
                    </div>
                  </div>

                  {/* Two-Factor Authentication */}
                  <div className="mb-8 p-6 bg-white/5 rounded-lg border border-white/10">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-1">
                          Two-Factor Authentication
                        </h3>
                        <p className="text-gray-400 text-sm">
                          Add an extra layer of security to your account
                        </p>
                      </div>
                      <button
                        onClick={() => setTwoFactorEnabled(!twoFactorEnabled)}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          twoFactorEnabled ? "bg-blue-500" : "bg-gray-600"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            twoFactorEnabled ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                    </div>
                    {twoFactorEnabled && (
                      <div className="mt-4 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                        <div className="flex items-center gap-2 text-green-400">
                          <Check className="w-5 h-5" />
                          <span className="font-medium">
                            2FA is enabled and active
                          </span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Biometric Authentication */}
                  <div className="mb-8 p-6 bg-white/5 rounded-lg border border-white/10">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-1">
                          Biometric Authentication
                        </h3>
                        <p className="text-gray-400 text-sm">
                          Use Face ID or Touch ID to unlock your vault
                        </p>
                      </div>
                      <button
                        onClick={() => setBiometricEnabled(!biometricEnabled)}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          biometricEnabled ? "bg-blue-500" : "bg-gray-600"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            biometricEnabled ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                    </div>
                  </div>

                  {/* Active Sessions */}
                  <div className="p-6 bg-white/5 rounded-lg border border-white/10">
                    <h3 className="text-lg font-semibold text-white mb-4">
                      Active Sessions
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                        <div className="flex items-center gap-3">
                          <Smartphone className="w-5 h-5 text-blue-400" />
                          <div>
                            <p className="text-white font-medium">
                              iPhone 15 Pro
                            </p>
                            <p className="text-gray-400 text-sm">
                              San Francisco, CA • Active now
                            </p>
                          </div>
                        </div>
                        <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                          Current
                        </span>
                      </div>
                      <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                        <div className="flex items-center gap-3">
                          <Smartphone className="w-5 h-5 text-gray-400" />
                          <div>
                            <p className="text-white font-medium">
                              MacBook Pro
                            </p>
                            <p className="text-gray-400 text-sm">
                              San Francisco, CA • 2 hours ago
                            </p>
                          </div>
                        </div>
                        <button className="px-3 py-1 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors">
                          Revoke
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Notifications Tab */}
              {activeTab === "notifications" && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">
                    Notification Settings
                  </h2>

                  <div className="space-y-4">
                    {[
                      {
                        title: "Security Alerts",
                        description: "Get notified about suspicious activity",
                        enabled: true,
                      },
                      {
                        title: "Password Expiration",
                        description: "Reminders when passwords need rotation",
                        enabled: true,
                      },
                      {
                        title: "Breach Alerts",
                        description: "Alerts when your passwords are compromised",
                        enabled: true,
                      },
                      {
                        title: "Product Updates",
                        description: "News about new features and improvements",
                        enabled: false,
                      },
                      {
                        title: "Marketing Emails",
                        description: "Promotional content and special offers",
                        enabled: false,
                      },
                    ].map((item, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10"
                      >
                        <div>
                          <h3 className="text-white font-medium mb-1">
                            {item.title}
                          </h3>
                          <p className="text-gray-400 text-sm">
                            {item.description}
                          </p>
                        </div>
                        <button
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            item.enabled ? "bg-blue-500" : "bg-gray-600"
                          }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              item.enabled ? "translate-x-6" : "translate-x-1"
                            }`}
                          />
                        </button>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Billing Tab */}
              {activeTab === "billing" && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">
                    Billing & Subscription
                  </h2>

                  {/* Current Plan */}
                  <div className="mb-6 p-6 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-lg border border-blue-500/30">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-xl font-bold text-white mb-1">
                          Premium Plan
                        </h3>
                        <p className="text-gray-300">$1.00 / month</p>
                      </div>
                      <span className="px-4 py-2 bg-green-500/20 text-green-400 rounded-full font-semibold">
                        Active
                      </span>
                    </div>
                    <p className="text-gray-300 mb-4">
                      Next billing date: February 15, 2024
                    </p>
                    <button className="px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors">
                      Manage Subscription
                    </button>
                  </div>

                  {/* Payment Method */}
                  <div className="mb-6 p-6 bg-white/5 rounded-lg border border-white/10">
                    <h3 className="text-lg font-semibold text-white mb-4">
                      Payment Method
                    </h3>
                    <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                      <div className="flex items-center gap-3">
                        <CreditCard className="w-8 h-8 text-blue-400" />
                        <div>
                          <p className="text-white font-medium">
                            •••• •••• •••• 4242
                          </p>
                          <p className="text-gray-400 text-sm">Expires 12/25</p>
                        </div>
                      </div>
                      <button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                        Update
                      </button>
                    </div>
                  </div>

                  {/* Billing History */}
                  <div className="p-6 bg-white/5 rounded-lg border border-white/10">
                    <h3 className="text-lg font-semibold text-white mb-4">
                      Billing History
                    </h3>
                    <div className="space-y-3">
                      {[
                        {
                          date: "Jan 15, 2024",
                          amount: "$1.00",
                          status: "Paid",
                        },
                        {
                          date: "Dec 15, 2023",
                          amount: "$1.00",
                          status: "Paid",
                        },
                        {
                          date: "Nov 15, 2023",
                          amount: "$1.00",
                          status: "Paid",
                        },
                      ].map((invoice, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-4 bg-white/5 rounded-lg"
                        >
                          <div>
                            <p className="text-white font-medium">
                              {invoice.date}
                            </p>
                            <p className="text-gray-400 text-sm">
                              Premium Plan
                            </p>
                          </div>
                          <div className="flex items-center gap-4">
                            <span className="text-white font-semibold">
                              {invoice.amount}
                            </span>
                            <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                              {invoice.status}
                            </span>
                            <button className="text-blue-400 hover:text-blue-300">
                              <Download className="w-5 h-5" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Family Tab */}
              {activeTab === "family" && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">
                    Family Sharing
                  </h2>

                  <div className="mb-6 p-6 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                    <p className="text-gray-300">
                      Upgrade to Family Plan to share your subscription with up to
                      5 family members for just $1/month total.
                    </p>
                    <button className="mt-4 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all">
                      Upgrade to Family Plan
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Data Tab */}
              {activeTab === "data" && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">
                    Data Management
                  </h2>

                  <div className="space-y-6">
                    {/* Export Data */}
                    <div className="p-6 bg-white/5 rounded-lg border border-white/10">
                      <h3 className="text-lg font-semibold text-white mb-2">
                        Export Your Data
                      </h3>
                      <p className="text-gray-400 mb-4">
                        Download all your passwords and data in encrypted format
                      </p>
                      <button className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2">
                        <Download className="w-5 h-5" />
                        Export Data
                      </button>
                    </div>

                    {/* Import Data */}
                    <div className="p-6 bg-white/5 rounded-lg border border-white/10">
                      <h3 className="text-lg font-semibold text-white mb-2">
                        Import Data
                      </h3>
                      <p className="text-gray-400 mb-4">
                        Import passwords from other password managers
                      </p>
                      <button className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2">
                        <Upload className="w-5 h-5" />
                        Import Data
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Danger Zone Tab */}
              {activeTab === "danger" && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">
                    Danger Zone
                  </h2>

                  <div className="space-y-6">
                    {/* Delete Account */}
                    <div className="p-6 bg-red-500/10 rounded-lg border border-red-500/20">
                      <h3 className="text-lg font-semibold text-red-400 mb-2">
                        Delete Account
                      </h3>
                      <p className="text-gray-400 mb-4">
                        Permanently delete your account and all associated data.
                        This action cannot be undone.
                      </p>
                      <button className="px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center gap-2">
                        <Trash2 className="w-5 h-5" />
                        Delete Account
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}