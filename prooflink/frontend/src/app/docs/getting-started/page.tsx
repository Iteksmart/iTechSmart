'use client';

import Link from 'next/link';
import {
  ArrowRight,
  Upload,
  Link2,
  CheckCircle,
  Code,
  Zap,
  Shield,
  Users,
  FileText,
  Key,
} from 'lucide-react';

export default function GettingStartedPage() {
  const steps = [
    {
      number: 1,
      title: 'Create Your Account',
      description: 'Sign up for ProofLink in less than 60 seconds',
      icon: Users,
      color: 'blue',
      details: [
        'Enter your email and password',
        'Verify your email address',
        'Complete your profile',
        'Start your free 7-day trial',
      ],
    },
    {
      number: 2,
      title: 'Upload Your First File',
      description: 'Create a cryptographic proof of any file',
      icon: Upload,
      color: 'green',
      details: [
        'Click "Create Proof" in the dashboard',
        'Drag and drop your file',
        'Wait for the hash to be generated',
        'Get your unique proof link',
      ],
    },
    {
      number: 3,
      title: 'Share & Verify',
      description: 'Share your proof link with anyone',
      icon: Link2,
      color: 'purple',
      details: [
        'Copy your proof link',
        'Share via email, messaging, or social media',
        'Recipients can verify without an account',
        'Track all verification attempts',
      ],
    },
  ];

  const features = [
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Create proofs in seconds with our optimized infrastructure',
    },
    {
      icon: Shield,
      title: 'Cryptographically Secure',
      description: 'SHA-256 hashing ensures mathematical certainty',
    },
    {
      icon: Code,
      title: 'Developer Friendly',
      description: 'Full REST API with comprehensive documentation',
    },
    {
      icon: FileText,
      title: 'All File Types',
      description: 'Support for documents, images, videos, and more',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-20">
        <div className="max-w-6xl mx-auto px-6">
          <h1 className="text-5xl font-bold mb-4">Getting Started with ProofLink</h1>
          <p className="text-xl text-blue-100 mb-8">
            Create your first cryptographic proof in under 5 minutes
          </p>
          <Link
            href="/auth/register"
            className="inline-flex items-center px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-blue-50 font-semibold text-lg"
          >
            Start Free Trial
            <ArrowRight className="w-5 h-5 ml-2" />
          </Link>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-16">
        {/* Quick Start Steps */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Three Simple Steps
          </h2>
          <div className="space-y-8">
            {steps.map((step) => {
              const Icon = step.icon;
              const colorClasses = {
                blue: 'from-blue-50 to-indigo-50 border-blue-100',
                green: 'from-green-50 to-emerald-50 border-green-100',
                purple: 'from-purple-50 to-pink-50 border-purple-100',
              };
              const iconColors = {
                blue: 'bg-blue-600',
                green: 'bg-green-600',
                purple: 'bg-purple-600',
              };

              return (
                <div
                  key={step.number}
                  className={`bg-gradient-to-br ${
                    colorClasses[step.color as keyof typeof colorClasses]
                  } rounded-xl p-8 border`}
                >
                  <div className="flex items-start gap-6">
                    {/* Step Number */}
                    <div className="flex-shrink-0">
                      <div
                        className={`w-16 h-16 ${
                          iconColors[step.color as keyof typeof iconColors]
                        } rounded-full flex items-center justify-center text-white text-2xl font-bold`}
                      >
                        {step.number}
                      </div>
                    </div>

                    {/* Content */}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <Icon className="w-6 h-6 text-gray-700" />
                        <h3 className="text-2xl font-bold text-gray-900">{step.title}</h3>
                      </div>
                      <p className="text-gray-700 mb-4 text-lg">{step.description}</p>
                      <ul className="space-y-2">
                        {step.details.map((detail, i) => (
                          <li key={i} className="flex items-center text-gray-700">
                            <CheckCircle className="w-5 h-5 text-green-600 mr-3 flex-shrink-0" />
                            {detail}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Features Grid */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Why Choose ProofLink?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-lg transition-shadow"
                >
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-blue-100 rounded-lg">
                      <Icon className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
                      <p className="text-gray-600">{feature.description}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Video Tutorial */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Watch the Tutorial
          </h2>
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="aspect-video bg-gradient-to-br from-blue-100 to-indigo-100 flex items-center justify-center">
              <div className="text-center">
                <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg
                    className="w-10 h-10 text-white"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>
                <p className="text-gray-700 font-medium">5-Minute Tutorial Video</p>
                <p className="text-gray-600 text-sm">Coming Soon</p>
              </div>
            </div>
          </div>
        </div>

        {/* API Quick Start */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            For Developers
          </h2>
          <div className="bg-gray-900 rounded-xl p-8 text-white">
            <div className="flex items-center gap-3 mb-6">
              <Key className="w-6 h-6" />
              <h3 className="text-xl font-bold">Quick API Example</h3>
            </div>
            <pre className="bg-gray-800 rounded-lg p-6 overflow-x-auto">
              <code className="text-sm">
{`# Install the SDK
pip install prooflink

# Create a proof
from prooflink import ProofLink

client = ProofLink(api_key="your_api_key")
proof = client.create_proof("document.pdf")

print(f"Proof Link: {proof.link}")
print(f"File Hash: {proof.hash}")

# Verify a file
result = client.verify_proof(
    proof_link="https://prooflink.ai/verify/abc123",
    file_path="document.pdf"
)

print(f"Valid: {result.is_valid}")`}
              </code>
            </pre>
            <div className="mt-6">
              <Link
                href="/docs/api"
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                View Full API Documentation
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-12 text-white text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of users who trust ProofLink for digital verification
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth/register"
              className="px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-blue-50 font-semibold text-lg"
            >
              Start Free Trial
            </Link>
            <Link
              href="/help"
              className="px-8 py-4 bg-white bg-opacity-20 text-white rounded-lg hover:bg-opacity-30 font-semibold text-lg"
            >
              View Help Center
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}