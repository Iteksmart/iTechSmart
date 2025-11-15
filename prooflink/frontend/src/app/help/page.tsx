'use client';

import Link from 'next/link';
import {
  BookOpen,
  FileText,
  Code,
  MessageCircle,
  Mail,
  ExternalLink,
  Search,
  ChevronRight,
  Shield,
  Zap,
  Users,
  HelpCircle,
} from 'lucide-react';
import { useState } from 'react';

export default function HelpPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const categories = [
    {
      icon: BookOpen,
      title: 'Getting Started',
      description: 'Learn the basics of ProofLink',
      color: 'blue',
      articles: [
        'Creating your first proof',
        'Understanding cryptographic hashing',
        'Verifying a proof',
        'Managing your account',
      ],
    },
    {
      icon: Code,
      title: 'API Documentation',
      description: 'Integrate ProofLink into your apps',
      color: 'purple',
      articles: [
        'API authentication',
        'Creating proofs via API',
        'Verifying proofs programmatically',
        'Webhooks and callbacks',
      ],
    },
    {
      icon: Shield,
      title: 'Security & Privacy',
      description: 'How we keep your data safe',
      color: 'green',
      articles: [
        'Data encryption',
        'Privacy policy',
        'GDPR compliance',
        'Two-factor authentication',
      ],
    },
    {
      icon: Zap,
      title: 'Advanced Features',
      description: 'Power user tips and tricks',
      color: 'orange',
      articles: [
        'Batch proof creation',
        'Custom integrations',
        'Automated workflows',
        'Export and reporting',
      ],
    },
  ];

  const faqs = [
    {
      question: 'What is a cryptographic proof?',
      answer:
        'A cryptographic proof is a mathematical guarantee that a file has not been altered. ProofLink uses SHA-256 hashing to create a unique fingerprint of your file that can be verified at any time.',
    },
    {
      question: 'How long are proofs stored?',
      answer:
        'Proofs are stored indefinitely as long as your account is active. You can delete proofs at any time from your dashboard.',
    },
    {
      question: 'Can I verify proofs without an account?',
      answer:
        'Yes! Anyone with a proof link can verify the authenticity of a file without creating an account. This makes it easy to share proofs with clients, partners, or the public.',
    },
    {
      question: 'What file types are supported?',
      answer:
        'ProofLink supports all file types. We create cryptographic hashes of the file content, so the file format doesn\'t matter.',
    },
    {
      question: 'Is my data secure?',
      answer:
        'Yes. We use industry-standard encryption for all data in transit and at rest. Your files are hashed locally before upload, and we never store the actual file content on our servers.',
    },
    {
      question: 'How much does ProofLink cost?',
      answer:
        'ProofLink costs just $1 per month for unlimited proofs, verifications, and API access. We believe digital trust should be affordable for everyone.',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-20">
        <div className="max-w-6xl mx-auto px-6">
          <h1 className="text-5xl font-bold mb-4">How can we help you?</h1>
          <p className="text-xl text-blue-100 mb-8">
            Search our knowledge base or browse categories below
          </p>
          
          {/* Search Bar */}
          <div className="max-w-2xl">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-6 h-6 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for help articles..."
                className="w-full pl-14 pr-4 py-4 rounded-xl text-gray-900 text-lg focus:ring-4 focus:ring-blue-300 focus:outline-none"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Categories Grid */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Browse by Category</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {categories.map((category, index) => {
              const Icon = category.icon;
              const colorClasses = {
                blue: 'from-blue-50 to-indigo-50 border-blue-100',
                purple: 'from-purple-50 to-pink-50 border-purple-100',
                green: 'from-green-50 to-emerald-50 border-green-100',
                orange: 'from-orange-50 to-amber-50 border-orange-100',
              };
              const iconColors = {
                blue: 'bg-blue-600',
                purple: 'bg-purple-600',
                green: 'bg-green-600',
                orange: 'bg-orange-600',
              };

              return (
                <div
                  key={index}
                  className={`bg-gradient-to-br ${colorClasses[category.color as keyof typeof colorClasses]} rounded-xl p-6 border hover:shadow-lg transition-shadow cursor-pointer`}
                >
                  <div className="flex items-start gap-4 mb-4">
                    <div className={`p-3 ${iconColors[category.color as keyof typeof iconColors]} rounded-lg`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-900 mb-1">{category.title}</h3>
                      <p className="text-gray-600">{category.description}</p>
                    </div>
                  </div>
                  <ul className="space-y-2">
                    {category.articles.map((article, i) => (
                      <li key={i}>
                        <a
                          href="#"
                          className="flex items-center text-gray-700 hover:text-blue-600 transition-colors"
                        >
                          <ChevronRight className="w-4 h-4 mr-2" />
                          {article}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>

        {/* FAQs */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Frequently Asked Questions</h2>
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <details
                key={index}
                className="bg-white rounded-xl border border-gray-100 overflow-hidden group"
              >
                <summary className="flex items-center justify-between p-6 cursor-pointer hover:bg-gray-50 transition-colors">
                  <div className="flex items-center gap-3">
                    <HelpCircle className="w-5 h-5 text-blue-600" />
                    <span className="font-semibold text-gray-900">{faq.question}</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400 group-open:rotate-90 transition-transform" />
                </summary>
                <div className="px-6 pb-6 text-gray-700 leading-relaxed">{faq.answer}</div>
              </details>
            ))}
          </div>
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <Link
            href="/docs/api"
            className="bg-white rounded-xl p-6 border border-gray-100 hover:shadow-lg transition-shadow"
          >
            <Code className="w-8 h-8 text-purple-600 mb-3" />
            <h3 className="text-lg font-bold text-gray-900 mb-2">API Documentation</h3>
            <p className="text-gray-600 mb-3">Complete API reference and integration guides</p>
            <span className="text-purple-600 font-medium flex items-center">
              View Docs <ExternalLink className="w-4 h-4 ml-2" />
            </span>
          </Link>

          <Link
            href="/docs/getting-started"
            className="bg-white rounded-xl p-6 border border-gray-100 hover:shadow-lg transition-shadow"
          >
            <BookOpen className="w-8 h-8 text-blue-600 mb-3" />
            <h3 className="text-lg font-bold text-gray-900 mb-2">Getting Started Guide</h3>
            <p className="text-gray-600 mb-3">Learn how to use ProofLink in 5 minutes</p>
            <span className="text-blue-600 font-medium flex items-center">
              Read Guide <ExternalLink className="w-4 h-4 ml-2" />
            </span>
          </Link>

          <Link
            href="/docs/security"
            className="bg-white rounded-xl p-6 border border-gray-100 hover:shadow-lg transition-shadow"
          >
            <Shield className="w-8 h-8 text-green-600 mb-3" />
            <h3 className="text-lg font-bold text-gray-900 mb-2">Security & Privacy</h3>
            <p className="text-gray-600 mb-3">How we protect your data and privacy</p>
            <span className="text-green-600 font-medium flex items-center">
              Learn More <ExternalLink className="w-4 h-4 ml-2" />
            </span>
          </Link>
        </div>

        {/* Contact Support */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-8 text-white">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-white bg-opacity-20 rounded-lg">
                <MessageCircle className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-2xl font-bold mb-1">Still need help?</h3>
                <p className="text-blue-100">Our support team is here to assist you</p>
              </div>
            </div>
            <div className="flex gap-3">
              <a
                href="mailto:support@prooflink.ai"
                className="px-6 py-3 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors flex items-center gap-2 font-semibold"
              >
                <Mail className="w-5 h-5" />
                Email Support
              </a>
              <button className="px-6 py-3 bg-white bg-opacity-20 text-white rounded-lg hover:bg-opacity-30 transition-colors flex items-center gap-2 font-semibold">
                <MessageCircle className="w-5 h-5" />
                Live Chat
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}