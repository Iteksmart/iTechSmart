"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Share2,
  Users,
  Mail,
  Check,
  X,
  Clock,
  Shield,
  Eye,
  Edit,
  Trash2,
  UserPlus,
  AlertCircle,
} from "lucide-react";

interface SharedItem {
  id: number;
  password_name: string;
  shared_with_email: string;
  shared_with_name: string;
  permissions: {
    can_view: boolean;
    can_edit: boolean;
    can_share: boolean;
  };
  status: "pending" | "accepted" | "rejected";
  created_at: string;
  accepted_at?: string;
}

interface SharedWithMe {
  id: number;
  password_name: string;
  owner_email: string;
  owner_name: string;
  permissions: {
    can_view: boolean;
    can_edit: boolean;
    can_share: boolean;
  };
  status: "pending" | "accepted" | "rejected";
  created_at: string;
}

export default function SharingPage() {
  const [activeTab, setActiveTab] = useState<"shared-by-me" | "shared-with-me">(
    "shared-by-me"
  );
  const [showShareModal, setShowShareModal] = useState(false);

  // Mock data - Shared by me
  const sharedByMe: SharedItem[] = [
    {
      id: 1,
      password_name: "Netflix Account",
      shared_with_email: "jane@example.com",
      shared_with_name: "Jane Doe",
      permissions: {
        can_view: true,
        can_edit: false,
        can_share: false,
      },
      status: "accepted",
      created_at: "2024-01-10T00:00:00Z",
      accepted_at: "2024-01-10T12:00:00Z",
    },
    {
      id: 2,
      password_name: "Spotify Premium",
      shared_with_email: "bob@example.com",
      shared_with_name: "Bob Smith",
      permissions: {
        can_view: true,
        can_edit: true,
        can_share: false,
      },
      status: "accepted",
      created_at: "2024-01-12T00:00:00Z",
      accepted_at: "2024-01-12T15:30:00Z",
    },
    {
      id: 3,
      password_name: "AWS Console",
      shared_with_email: "alice@example.com",
      shared_with_name: "Alice Johnson",
      permissions: {
        can_view: true,
        can_edit: false,
        can_share: false,
      },
      status: "pending",
      created_at: "2024-01-14T00:00:00Z",
    },
  ];

  // Mock data - Shared with me
  const sharedWithMe: SharedWithMe[] = [
    {
      id: 1,
      password_name: "Company VPN",
      owner_email: "admin@company.com",
      owner_name: "IT Admin",
      permissions: {
        can_view: true,
        can_edit: false,
        can_share: false,
      },
      status: "accepted",
      created_at: "2024-01-08T00:00:00Z",
    },
    {
      id: 2,
      password_name: "Shared Drive",
      owner_email: "manager@company.com",
      owner_name: "Team Manager",
      permissions: {
        can_view: true,
        can_edit: true,
        can_share: false,
      },
      status: "accepted",
      created_at: "2024-01-11T00:00:00Z",
    },
    {
      id: 3,
      password_name: "Project Database",
      owner_email: "dev@company.com",
      owner_name: "Dev Team",
      permissions: {
        can_view: true,
        can_edit: false,
        can_share: false,
      },
      status: "pending",
      created_at: "2024-01-15T00:00:00Z",
    },
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "accepted":
        return (
          <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-semibold flex items-center gap-1">
            <Check className="w-3 h-3" />
            Accepted
          </span>
        );
      case "pending":
        return (
          <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-xs font-semibold flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Pending
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Sharing</h1>
          <p className="text-gray-400">
            Share passwords securely with team members and family
          </p>
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
                <p className="text-gray-400 text-sm">Shared by Me</p>
                <p className="text-2xl font-bold text-white">
                  {sharedByMe.length}
                </p>
              </div>
              <Share2 className="w-8 h-8 text-blue-400" />
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
                <p className="text-gray-400 text-sm">Shared with Me</p>
                <p className="text-2xl font-bold text-white">
                  {sharedWithMe.length}
                </p>
              </div>
              <Users className="w-8 h-8 text-purple-400" />
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
                <p className="text-gray-400 text-sm">Pending Invites</p>
                <p className="text-2xl font-bold text-yellow-400">
                  {[...sharedByMe, ...sharedWithMe].filter(
                    (s) => s.status === "pending"
                  ).length}
                </p>
              </div>
              <Clock className="w-8 h-8 text-yellow-400" />
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
                <p className="text-gray-400 text-sm">Active Shares</p>
                <p className="text-2xl font-bold text-green-400">
                  {[...sharedByMe, ...sharedWithMe].filter(
                    (s) => s.status === "accepted"
                  ).length}
                </p>
              </div>
              <Check className="w-8 h-8 text-green-400" />
            </div>
          </motion.div>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab("shared-by-me")}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === "shared-by-me"
                ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white"
                : "bg-white/5 text-gray-400 hover:bg-white/10"
            }`}
          >
            Shared by Me
          </button>
          <button
            onClick={() => setActiveTab("shared-with-me")}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === "shared-with-me"
                ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white"
                : "bg-white/5 text-gray-400 hover:bg-white/10"
            }`}
          >
            Shared with Me
          </button>
          <button
            onClick={() => setShowShareModal(true)}
            className="ml-auto px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all flex items-center gap-2"
          >
            <UserPlus className="w-5 h-5" />
            Share Password
          </button>
        </div>

        {/* Shared by Me */}
        {activeTab === "shared-by-me" && (
          <div className="space-y-4">
            {sharedByMe.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                      <Shield className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-white mb-1">
                        {item.password_name}
                      </h3>
                      <div className="flex items-center gap-2 text-gray-400 text-sm">
                        <Mail className="w-4 h-4" />
                        <span>Shared with {item.shared_with_name}</span>
                        <span className="text-gray-600">•</span>
                        <span>{item.shared_with_email}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(item.status)}
                    <button className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors">
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {/* Permissions */}
                <div className="flex gap-2 mb-4">
                  {item.permissions.can_view && (
                    <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-medium flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      View
                    </span>
                  )}
                  {item.permissions.can_edit && (
                    <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-xs font-medium flex items-center gap-1">
                      <Edit className="w-3 h-3" />
                      Edit
                    </span>
                  )}
                  {item.permissions.can_share && (
                    <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-medium flex items-center gap-1">
                      <Share2 className="w-3 h-3" />
                      Share
                    </span>
                  )}
                </div>

                {/* Metadata */}
                <div className="flex items-center gap-4 text-sm text-gray-400">
                  <span>
                    Shared on {new Date(item.created_at).toLocaleDateString()}
                  </span>
                  {item.accepted_at && (
                    <>
                      <span className="text-gray-600">•</span>
                      <span>
                        Accepted on{" "}
                        {new Date(item.accepted_at).toLocaleDateString()}
                      </span>
                    </>
                  )}
                </div>
              </motion.div>
            ))}

            {sharedByMe.length === 0 && (
              <div className="text-center py-12">
                <Share2 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  No Shared Passwords
                </h3>
                <p className="text-gray-400 mb-6">
                  Start sharing passwords with your team or family
                </p>
                <button
                  onClick={() => setShowShareModal(true)}
                  className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all inline-flex items-center gap-2"
                >
                  <UserPlus className="w-5 h-5" />
                  Share Your First Password
                </button>
              </div>
            )}
          </div>
        )}

        {/* Shared with Me */}
        {activeTab === "shared-with-me" && (
          <div className="space-y-4">
            {sharedWithMe.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                      <Shield className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-white mb-1">
                        {item.password_name}
                      </h3>
                      <div className="flex items-center gap-2 text-gray-400 text-sm">
                        <Users className="w-4 h-4" />
                        <span>Shared by {item.owner_name}</span>
                        <span className="text-gray-600">•</span>
                        <span>{item.owner_email}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(item.status)}
                    {item.status === "pending" && (
                      <>
                        <button className="px-4 py-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors flex items-center gap-2">
                          <Check className="w-4 h-4" />
                          Accept
                        </button>
                        <button className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors flex items-center gap-2">
                          <X className="w-4 h-4" />
                          Decline
                        </button>
                      </>
                    )}
                  </div>
                </div>

                {/* Permissions */}
                <div className="flex gap-2 mb-4">
                  {item.permissions.can_view && (
                    <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-medium flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      View
                    </span>
                  )}
                  {item.permissions.can_edit && (
                    <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-xs font-medium flex items-center gap-1">
                      <Edit className="w-3 h-3" />
                      Edit
                    </span>
                  )}
                  {item.permissions.can_share && (
                    <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-medium flex items-center gap-1">
                      <Share2 className="w-3 h-3" />
                      Share
                    </span>
                  )}
                </div>

                {/* Metadata */}
                <div className="text-sm text-gray-400">
                  Shared on {new Date(item.created_at).toLocaleDateString()}
                </div>
              </motion.div>
            ))}

            {sharedWithMe.length === 0 && (
              <div className="text-center py-12">
                <Users className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  No Shared Passwords
                </h3>
                <p className="text-gray-400">
                  You don't have any passwords shared with you yet
                </p>
              </div>
            )}
          </div>
        )}

        {/* Share Modal */}
        {showShareModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-slate-900 rounded-xl p-6 max-w-md w-full border border-white/20"
            >
              <h2 className="text-2xl font-bold text-white mb-4">
                Share Password
              </h2>

              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-gray-400 mb-2">
                    Select Password
                  </label>
                  <select className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-blue-500">
                    <option value="">Choose a password...</option>
                    <option value="1">Netflix Account</option>
                    <option value="2">Spotify Premium</option>
                    <option value="3">AWS Console</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">
                    Share with (Email)
                  </label>
                  <input
                    type="email"
                    placeholder="user@example.com"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Permissions</label>
                  <div className="space-y-2">
                    <label className="flex items-center gap-2 text-white">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="w-4 h-4 rounded border-white/20 bg-white/5"
                      />
                      <span className="text-sm">Can view password</span>
                    </label>
                    <label className="flex items-center gap-2 text-white">
                      <input
                        type="checkbox"
                        className="w-4 h-4 rounded border-white/20 bg-white/5"
                      />
                      <span className="text-sm">Can edit password</span>
                    </label>
                    <label className="flex items-center gap-2 text-white">
                      <input
                        type="checkbox"
                        className="w-4 h-4 rounded border-white/20 bg-white/5"
                      />
                      <span className="text-sm">Can share with others</span>
                    </label>
                  </div>
                </div>

                <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                  <div className="flex items-start gap-2 text-blue-400 text-sm">
                    <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    <p>
                      The recipient will receive an email invitation to accept
                      this shared password.
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowShareModal(false)}
                  className="flex-1 px-4 py-3 bg-white/5 text-white rounded-lg hover:bg-white/10 transition-colors"
                >
                  Cancel
                </button>
                <button className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all">
                  Share Password
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
}