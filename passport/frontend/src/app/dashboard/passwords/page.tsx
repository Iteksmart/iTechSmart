"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Search,
  Plus,
  Filter,
  Grid,
  List,
  Star,
  Globe,
  CreditCard,
  FileText,
  Shield,
  AlertTriangle,
  Eye,
  EyeOff,
  Copy,
  Edit,
  Trash2,
  MoreVertical,
} from "lucide-react";

interface Password {
  id: number;
  name: string;
  type: string;
  username?: string;
  url?: string;
  folder?: string;
  strength: "weak" | "fair" | "good" | "strong";
  is_favorite: boolean;
  is_compromised: boolean;
  last_used_at?: string;
  created_at: string;
}

export default function PasswordsPage() {
  const [view, setView] = useState<"grid" | "list">("grid");
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [showPassword, setShowPassword] = useState<number | null>(null);

  // Mock data
  const passwords: Password[] = [
    {
      id: 1,
      name: "Gmail",
      type: "login",
      username: "user@gmail.com",
      url: "https://gmail.com",
      folder: "Email",
      strength: "strong",
      is_favorite: true,
      is_compromised: false,
      last_used_at: "2024-01-15T10:30:00Z",
      created_at: "2024-01-01T00:00:00Z",
    },
    {
      id: 2,
      name: "Netflix",
      type: "login",
      username: "user@email.com",
      url: "https://netflix.com",
      folder: "Entertainment",
      strength: "good",
      is_favorite: true,
      is_compromised: false,
      last_used_at: "2024-01-14T20:15:00Z",
      created_at: "2024-01-02T00:00:00Z",
    },
    {
      id: 3,
      name: "Bank of America",
      type: "login",
      username: "john.doe",
      url: "https://bankofamerica.com",
      folder: "Finance",
      strength: "strong",
      is_favorite: false,
      is_compromised: false,
      last_used_at: "2024-01-13T09:00:00Z",
      created_at: "2024-01-03T00:00:00Z",
    },
    {
      id: 4,
      name: "Visa Card",
      type: "card",
      username: "John Doe",
      folder: "Finance",
      strength: "strong",
      is_favorite: false,
      is_compromised: false,
      created_at: "2024-01-04T00:00:00Z",
    },
    {
      id: 5,
      name: "Old Facebook",
      type: "login",
      username: "user@email.com",
      url: "https://facebook.com",
      folder: "Social",
      strength: "weak",
      is_favorite: false,
      is_compromised: true,
      last_used_at: "2023-12-01T00:00:00Z",
      created_at: "2023-01-01T00:00:00Z",
    },
  ];

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "login":
        return <Globe className="w-5 h-5" />;
      case "card":
        return <CreditCard className="w-5 h-5" />;
      case "note":
        return <FileText className="w-5 h-5" />;
      default:
        return <Shield className="w-5 h-5" />;
    }
  };

  const getStrengthColor = (strength: string) => {
    switch (strength) {
      case "weak":
        return "text-red-500";
      case "fair":
        return "text-orange-500";
      case "good":
        return "text-yellow-500";
      case "strong":
        return "text-green-500";
      default:
        return "text-gray-500";
    }
  };

  const filteredPasswords = passwords.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.username?.toLowerCase().includes(search.toLowerCase()) ||
      p.url?.toLowerCase().includes(search.toLowerCase());

    const matchesFilter =
      filter === "all" ||
      (filter === "favorites" && p.is_favorite) ||
      (filter === "weak" && p.strength === "weak") ||
      (filter === "compromised" && p.is_compromised) ||
      (filter === p.type);

    return matchesSearch && matchesFilter;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">My Passwords</h1>
          <p className="text-gray-400">
            Manage your passwords, cards, and secure notes
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
                <p className="text-gray-400 text-sm">Total Items</p>
                <p className="text-2xl font-bold text-white">{passwords.length}</p>
              </div>
              <Shield className="w-8 h-8 text-blue-400" />
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
                <p className="text-gray-400 text-sm">Favorites</p>
                <p className="text-2xl font-bold text-white">
                  {passwords.filter((p) => p.is_favorite).length}
                </p>
              </div>
              <Star className="w-8 h-8 text-yellow-400" />
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
                <p className="text-gray-400 text-sm">Weak Passwords</p>
                <p className="text-2xl font-bold text-orange-400">
                  {passwords.filter((p) => p.strength === "weak").length}
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
                <p className="text-gray-400 text-sm">Compromised</p>
                <p className="text-2xl font-bold text-red-400">
                  {passwords.filter((p) => p.is_compromised).length}
                </p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-400" />
            </div>
          </motion.div>
        </div>

        {/* Toolbar */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search passwords..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* Filter */}
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Items</option>
              <option value="favorites">Favorites</option>
              <option value="login">Logins</option>
              <option value="card">Cards</option>
              <option value="note">Notes</option>
              <option value="weak">Weak Passwords</option>
              <option value="compromised">Compromised</option>
            </select>

            {/* View Toggle */}
            <div className="flex gap-2">
              <button
                onClick={() => setView("grid")}
                className={`p-2 rounded-lg ${
                  view === "grid"
                    ? "bg-blue-500 text-white"
                    : "bg-white/5 text-gray-400"
                }`}
              >
                <Grid className="w-5 h-5" />
              </button>
              <button
                onClick={() => setView("list")}
                className={`p-2 rounded-lg ${
                  view === "list"
                    ? "bg-blue-500 text-white"
                    : "bg-white/5 text-gray-400"
                }`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>

            {/* Add Button */}
            <button className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Add Password
            </button>
          </div>
        </div>

        {/* Password Grid/List */}
        {view === "grid" ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredPasswords.map((password, index) => (
              <motion.div
                key={password.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:border-blue-500/50 transition-all group"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                      {getTypeIcon(password.type)}
                    </div>
                    <div>
                      <h3 className="text-white font-semibold">{password.name}</h3>
                      {password.username && (
                        <p className="text-gray-400 text-sm">{password.username}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {password.is_favorite && (
                      <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                    )}
                    {password.is_compromised && (
                      <AlertTriangle className="w-4 h-4 text-red-400" />
                    )}
                  </div>
                </div>

                {/* Details */}
                {password.url && (
                  <p className="text-gray-400 text-sm mb-2 truncate">
                    {password.url}
                  </p>
                )}
                {password.folder && (
                  <span className="inline-block px-2 py-1 bg-white/5 rounded text-xs text-gray-400 mb-4">
                    {password.folder}
                  </span>
                )}

                {/* Strength */}
                <div className="flex items-center gap-2 mb-4">
                  <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        password.strength === "weak"
                          ? "w-1/4 bg-red-500"
                          : password.strength === "fair"
                          ? "w-1/2 bg-orange-500"
                          : password.strength === "good"
                          ? "w-3/4 bg-yellow-500"
                          : "w-full bg-green-500"
                      }`}
                    />
                  </div>
                  <span
                    className={`text-xs font-semibold ${getStrengthColor(
                      password.strength
                    )}`}
                  >
                    {password.strength}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button className="flex-1 px-3 py-2 bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30 transition-colors flex items-center justify-center gap-2">
                    <Eye className="w-4 h-4" />
                    View
                  </button>
                  <button className="px-3 py-2 bg-white/5 text-gray-400 rounded-lg hover:bg-white/10 transition-colors">
                    <Copy className="w-4 h-4" />
                  </button>
                  <button className="px-3 py-2 bg-white/5 text-gray-400 rounded-lg hover:bg-white/10 transition-colors">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button className="px-3 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 overflow-hidden">
            <table className="w-full">
              <thead className="bg-white/5">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Username
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Folder
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Strength
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Last Used
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {filteredPasswords.map((password) => (
                  <tr key={password.id} className="hover:bg-white/5">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                          {getTypeIcon(password.type)}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-white font-medium">
                              {password.name}
                            </span>
                            {password.is_favorite && (
                              <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                            )}
                            {password.is_compromised && (
                              <AlertTriangle className="w-4 h-4 text-red-400" />
                            )}
                          </div>
                          {password.url && (
                            <span className="text-gray-400 text-sm">
                              {password.url}
                            </span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-400">
                      {password.username || "-"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {password.folder && (
                        <span className="px-2 py-1 bg-white/5 rounded text-xs text-gray-400">
                          {password.folder}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`text-sm font-semibold ${getStrengthColor(
                          password.strength
                        )}`}
                      >
                        {password.strength}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-400 text-sm">
                      {password.last_used_at
                        ? new Date(password.last_used_at).toLocaleDateString()
                        : "Never"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button className="p-2 text-gray-400 hover:text-blue-400 transition-colors">
                          <Eye className="w-4 h-4" />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-blue-400 transition-colors">
                          <Copy className="w-4 h-4" />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-blue-400 transition-colors">
                          <Edit className="w-4 h-4" />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-red-400 transition-colors">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Empty State */}
        {filteredPasswords.length === 0 && (
          <div className="text-center py-12">
            <Shield className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">
              No passwords found
            </h3>
            <p className="text-gray-400 mb-6">
              {search || filter !== "all"
                ? "Try adjusting your search or filters"
                : "Get started by adding your first password"}
            </p>
            {!search && filter === "all" && (
              <button className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all inline-flex items-center gap-2">
                <Plus className="w-5 h-5" />
                Add Your First Password
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}