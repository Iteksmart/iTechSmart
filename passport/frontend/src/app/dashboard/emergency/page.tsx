"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Heart,
  UserPlus,
  Clock,
  Shield,
  AlertTriangle,
  Check,
  X,
  Mail,
  Calendar,
  Info,
} from "lucide-react";

interface EmergencyContact {
  id: number;
  grantee_name: string;
  grantee_email: string;
  delay_hours: number;
  access_level: "view" | "takeover";
  status: "active" | "pending" | "requested";
  created_at: string;
  requested_at?: string;
  granted_at?: string;
}

interface EmergencyRequest {
  id: number;
  grantor_name: string;
  grantor_email: string;
  delay_hours: number;
  access_level: "view" | "takeover";
  status: "pending" | "approved" | "rejected";
  requested_at: string;
  available_at?: string;
}

export default function EmergencyAccessPage() {
  const [showAddModal, setShowAddModal] = useState(false);

  // Mock data - Trusted contacts
  const trustedContacts: EmergencyContact[] = [
    {
      id: 1,
      grantee_name: "Jane Doe",
      grantee_email: "jane@example.com",
      delay_hours: 48,
      access_level: "view",
      status: "active",
      created_at: "2024-01-01T00:00:00Z",
    },
    {
      id: 2,
      grantee_name: "Bob Smith",
      grantee_email: "bob@example.com",
      delay_hours: 72,
      access_level: "takeover",
      status: "active",
      created_at: "2024-01-05T00:00:00Z",
    },
    {
      id: 3,
      grantee_name: "Alice Johnson",
      grantee_email: "alice@example.com",
      delay_hours: 24,
      access_level: "view",
      status: "requested",
      created_at: "2024-01-10T00:00:00Z",
      requested_at: "2024-01-15T10:00:00Z",
    },
  ];

  // Mock data - Emergency requests
  const emergencyRequests: EmergencyRequest[] = [
    {
      id: 1,
      grantor_name: "John Manager",
      grantor_email: "john@company.com",
      delay_hours: 48,
      access_level: "view",
      status: "pending",
      requested_at: "2024-01-14T00:00:00Z",
      available_at: "2024-01-16T00:00:00Z",
    },
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return (
          <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-semibold flex items-center gap-1">
            <Check className="w-3 h-3" />
            Active
          </span>
        );
      case "pending":
        return (
          <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-xs font-semibold flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Pending
          </span>
        );
      case "requested":
        return (
          <span className="px-3 py-1 bg-orange-500/20 text-orange-400 rounded-full text-xs font-semibold flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            Requested
          </span>
        );
      case "approved":
        return (
          <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-semibold flex items-center gap-1">
            <Check className="w-3 h-3" />
            Approved
          </span>
        );
      case "rejected":
        return (
          <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-xs font-semibold flex items-center gap-1">
            <X className="w-3 h-3" />
            Rejected
          </span>
        );
    }
  };

  const getAccessLevelBadge = (level: string) => {
    switch (level) {
      case "view":
        return (
          <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-medium">
            View Only
          </span>
        );
      case "takeover":
        return (
          <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-xs font-medium">
            Full Takeover
          </span>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Emergency Access
          </h1>
          <p className="text-gray-400">
            Grant trusted contacts access to your vault in case of emergency
          </p>
        </div>

        {/* Info Banner */}
        <div className="mb-6 p-6 bg-blue-500/10 border border-blue-500/20 rounded-xl">
          <div className="flex items-start gap-4">
            <Info className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                How Emergency Access Works
              </h3>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  <span>
                    Designate trusted contacts who can request emergency access
                    to your vault
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  <span>
                    When they request access, you'll be notified and have a
                    waiting period to reject
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  <span>
                    If you don't respond within the waiting period, they'll
                    automatically gain access
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  <span>
                    Choose between "View Only" (read passwords) or "Full
                    Takeover" (change master password)
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Trusted Contacts</p>
                <p className="text-2xl font-bold text-white">
                  {trustedContacts.length}
                </p>
              </div>
              <Heart className="w-8 h-8 text-red-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Active</p>
                <p className="text-2xl font-bold text-green-400">
                  {trustedContacts.filter((c) => c.status === "active").length}
                </p>
              </div>
              <Check className="w-8 h-8 text-green-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Pending Requests</p>
                <p className="text-2xl font-bold text-orange-400">
                  {trustedContacts.filter((c) => c.status === "requested").length}
                </p>
              </div>
              <AlertTriangle className="w-8 h-8 text-orange-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">My Requests</p>
                <p className="text-2xl font-bold text-blue-400">
                  {emergencyRequests.length}
                </p>
              </div>
              <Clock className="w-8 h-8 text-blue-400" />
            </div>
          </motion.div>
        </div>

        {/* Add Contact Button */}
        <div className="mb-6">
          <button
            onClick={() => setShowAddModal(true)}
            className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all flex items-center gap-2"
          >
            <UserPlus className="w-5 h-5" />
            Add Trusted Contact
          </button>
        </div>

        {/* Trusted Contacts */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">
            My Trusted Contacts
          </h2>
          <div className="space-y-4">
            {trustedContacts.map((contact, index) => (
              <motion.div
                key={contact.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-pink-500 rounded-full flex items-center justify-center">
                      <Heart className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-white mb-1">
                        {contact.grantee_name}
                      </h3>
                      <div className="flex items-center gap-2 text-gray-400 text-sm">
                        <Mail className="w-4 h-4" />
                        <span>{contact.grantee_email}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(contact.status)}
                    {contact.status === "requested" && (
                      <>
                        <button className="px-4 py-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors">
                          Approve
                        </button>
                        <button className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors">
                          Reject
                        </button>
                      </>
                    )}
                    {contact.status === "active" && (
                      <button className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors">
                        Revoke
                      </button>
                    )}
                  </div>
                </div>

                {/* Details */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-white/5 rounded-lg">
                  <div>
                    <p className="text-gray-400 text-sm mb-1">Waiting Period</p>
                    <div className="flex items-center gap-2 text-white font-medium">
                      <Clock className="w-4 h-4 text-blue-400" />
                      <span>{contact.delay_hours} hours</span>
                    </div>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm mb-1">Access Level</p>
                    <div>{getAccessLevelBadge(contact.access_level)}</div>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm mb-1">Added On</p>
                    <div className="flex items-center gap-2 text-white font-medium">
                      <Calendar className="w-4 h-4 text-purple-400" />
                      <span>
                        {new Date(contact.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Request Alert */}
                {contact.status === "requested" && contact.requested_at && (
                  <div className="mt-4 p-4 bg-orange-500/10 border border-orange-500/20 rounded-lg">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-orange-400 font-semibold mb-1">
                          Emergency Access Requested
                        </p>
                        <p className="text-gray-300 text-sm">
                          Requested on{" "}
                          {new Date(contact.requested_at).toLocaleString()}. If
                          you don't respond within {contact.delay_hours} hours,
                          access will be automatically granted.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </motion.div>
            ))}

            {trustedContacts.length === 0 && (
              <div className="text-center py-12 bg-white/5 rounded-xl border border-white/10">
                <Heart className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  No Trusted Contacts
                </h3>
                <p className="text-gray-400 mb-6">
                  Add trusted contacts who can access your vault in emergencies
                </p>
                <button
                  onClick={() => setShowAddModal(true)}
                  className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all inline-flex items-center gap-2"
                >
                  <UserPlus className="w-5 h-5" />
                  Add Your First Trusted Contact
                </button>
              </div>
            )}
          </div>
        </div>

        {/* My Emergency Requests */}
        {emergencyRequests.length > 0 && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-4">
              My Emergency Requests
            </h2>
            <div className="space-y-4">
              {emergencyRequests.map((request, index) => (
                <motion.div
                  key={request.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                        <Shield className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-xl font-semibold text-white mb-1">
                          {request.grantor_name}'s Vault
                        </h3>
                        <div className="flex items-center gap-2 text-gray-400 text-sm">
                          <Mail className="w-4 h-4" />
                          <span>{request.grantor_email}</span>
                        </div>
                      </div>
                    </div>
                    {getStatusBadge(request.status)}
                  </div>

                  {/* Details */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-white/5 rounded-lg mb-4">
                    <div>
                      <p className="text-gray-400 text-sm mb-1">Requested</p>
                      <div className="text-white font-medium">
                        {new Date(request.requested_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div>
                      <p className="text-gray-400 text-sm mb-1">
                        Available After
                      </p>
                      <div className="text-white font-medium">
                        {request.available_at
                          ? new Date(request.available_at).toLocaleDateString()
                          : "Pending approval"}
                      </div>
                    </div>
                    <div>
                      <p className="text-gray-400 text-sm mb-1">Access Level</p>
                      <div>{getAccessLevelBadge(request.access_level)}</div>
                    </div>
                  </div>

                  {/* Waiting Alert */}
                  {request.status === "pending" && request.available_at && (
                    <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                      <div className="flex items-start gap-3">
                        <Clock className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-blue-400 font-semibold mb-1">
                            Waiting Period Active
                          </p>
                          <p className="text-gray-300 text-sm">
                            Access will be automatically granted on{" "}
                            {new Date(request.available_at).toLocaleString()} if
                            not rejected by the owner.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Add Contact Modal */}
        {showAddModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-slate-900 rounded-xl p-6 max-w-md w-full border border-white/20"
            >
              <h2 className="text-2xl font-bold text-white mb-4">
                Add Trusted Contact
              </h2>

              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-gray-400 mb-2">
                    Contact Email
                  </label>
                  <input
                    type="email"
                    placeholder="trusted@example.com"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">
                    Waiting Period (hours)
                  </label>
                  <select className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-blue-500">
                    <option value="24">24 hours</option>
                    <option value="48">48 hours</option>
                    <option value="72">72 hours (3 days)</option>
                    <option value="168">168 hours (7 days)</option>
                  </select>
                  <p className="text-gray-400 text-sm mt-2">
                    Time you have to reject their emergency access request
                  </p>
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Access Level</label>
                  <select className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-blue-500">
                    <option value="view">View Only</option>
                    <option value="takeover">Full Takeover</option>
                  </select>
                  <p className="text-gray-400 text-sm mt-2">
                    View Only: Can read passwords. Full Takeover: Can change
                    master password
                  </p>
                </div>

                <div className="p-4 bg-orange-500/10 border border-orange-500/20 rounded-lg">
                  <div className="flex items-start gap-2 text-orange-400 text-sm">
                    <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    <p>
                      Only add people you completely trust. They will be able to
                      request access to your entire vault.
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 px-4 py-3 bg-white/5 text-white rounded-lg hover:bg-white/10 transition-colors"
                >
                  Cancel
                </button>
                <button className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all">
                  Add Contact
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
}