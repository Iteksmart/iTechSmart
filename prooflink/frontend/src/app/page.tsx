/**
 * Landing Page - ProofLink.AI
 */

'use client';

import Link from 'next/link';
import { Shield, Zap, Lock, CheckCircle, ArrowRight, Star, Users, Globe } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-gray-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-primary-600" />
              <span className="text-2xl font-bold gradient-text">ProofLink.AI</span>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <Link href="#features" className="text-gray-600 hover:text-primary-600 transition">
                Features
              </Link>
              <Link href="#pricing" className="text-gray-600 hover:text-primary-600 transition">
                Pricing
              </Link>
              <Link href="#how-it-works" className="text-gray-600 hover:text-primary-600 transition">
                How It Works
              </Link>
              <Link href="/docs" className="text-gray-600 hover:text-primary-600 transition">
                Docs
              </Link>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link href="/auth/login" className="text-gray-600 hover:text-primary-600 transition">
                Login
              </Link>
              <Link href="/auth/register" className="btn btn-primary">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center space-x-2 bg-primary-100 text-primary-700 px-4 py-2 rounded-full mb-8">
            <Star className="h-4 w-4" />
            <span className="text-sm font-medium">The World's Trust Layer</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6">
            Proof, made <span className="gradient-text">simple</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Verify anything digital in seconds — no blockchain, no nonsense.
            <br />
            Just <span className="font-bold text-primary-600">$1 for digital truth</span>.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4 mb-12">
            <Link href="/auth/register" className="btn btn-primary text-lg px-8 py-4">
              Start Free Trial
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
            <Link href="/verify" className="btn btn-outline text-lg px-8 py-4">
              Verify a Proof
            </Link>
          </div>
          
          <div className="flex items-center justify-center space-x-8 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span>No credit card required</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span>10 free proofs</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span>Cancel anytime</span>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-white/50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">1M+</div>
              <div className="text-gray-600">Proofs Created</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">50K+</div>
              <div className="text-gray-600">Active Users</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">99.9%</div>
              <div className="text-gray-600">Uptime</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">$1</div>
              <div className="text-gray-600">Per Month</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything you need to prove digital truth
            </h2>
            <p className="text-xl text-gray-600">
              Powerful features that make verification instant and universal
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="card p-8 hover:shadow-lg transition">
              <div className="bg-primary-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Instant Verification</h3>
              <p className="text-gray-600">
                Create and verify proofs in seconds. No complex setup, no waiting.
              </p>
            </div>
            
            {/* Feature 2 */}
            <div className="card p-8 hover:shadow-lg transition">
              <div className="bg-primary-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Lock className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Zero-Knowledge Security</h3>
              <p className="text-gray-600">
                Your data never leaves your device. Only hashes are stored.
              </p>
            </div>
            
            {/* Feature 3 */}
            <div className="card p-8 hover:shadow-lg transition">
              <div className="bg-primary-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Globe className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Universal Access</h3>
              <p className="text-gray-600">
                Anyone can verify your proofs. No account needed for verification.
              </p>
            </div>
            
            {/* Feature 4 */}
            <div className="card p-8 hover:shadow-lg transition">
              <div className="bg-primary-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">AI-Powered Detection</h3>
              <p className="text-gray-600">
                Advanced AI detects tampering and manipulation automatically.
              </p>
            </div>
            
            {/* Feature 5 */}
            <div className="card p-8 hover:shadow-lg transition">
              <div className="bg-primary-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Users className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Team Collaboration</h3>
              <p className="text-gray-600">
                Share proofs with your team. Manage permissions and access.
              </p>
            </div>
            
            {/* Feature 6 */}
            <div className="card p-8 hover:shadow-lg transition">
              <div className="bg-primary-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <CheckCircle className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">API Access</h3>
              <p className="text-gray-600">
                Integrate ProofLink into your apps with our powerful API.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-4 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Simple, transparent pricing
            </h2>
            <p className="text-xl text-gray-600">
              Choose the plan that's right for you
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Free Plan */}
            <div className="card p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Free</h3>
              <div className="text-4xl font-bold text-gray-900 mb-4">$0</div>
              <p className="text-gray-600 mb-6">Perfect for trying out</p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>10 proofs/month</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>10MB file limit</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Basic verification</span>
                </li>
              </ul>
              <Link href="/auth/register" className="btn btn-outline w-full">
                Get Started
              </Link>
            </div>
            
            {/* Monthly Plan */}
            <div className="card p-8 border-2 border-primary-500 relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-primary-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                Popular
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Monthly</h3>
              <div className="text-4xl font-bold text-gray-900 mb-4">$1</div>
              <p className="text-gray-600 mb-6">Best for individuals</p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Unlimited proofs</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>100MB file limit</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>AI verification</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>API access</span>
                </li>
              </ul>
              <Link href="/auth/register" className="btn btn-primary w-full">
                Start Free Trial
              </Link>
            </div>
            
            {/* Yearly Plan */}
            <div className="card p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Yearly</h3>
              <div className="text-4xl font-bold text-gray-900 mb-4">$10</div>
              <p className="text-gray-600 mb-6">Save $2/year</p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Everything in Monthly</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Priority support</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Custom branding</span>
                </li>
              </ul>
              <Link href="/auth/register" className="btn btn-outline w-full">
                Get Started
              </Link>
            </div>
            
            {/* Lifetime Plan */}
            <div className="card p-8 bg-gradient-to-br from-purple-50 to-blue-50">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Lifetime</h3>
              <div className="text-4xl font-bold text-gray-900 mb-4">$5</div>
              <p className="text-gray-600 mb-6">One-time payment</p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>All Premium features</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Lifetime access</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Best value!</span>
                </li>
              </ul>
              <Link href="/auth/register" className="btn btn-primary w-full">
                Get Lifetime Access
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            Ready to start proving digital truth?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Join thousands of users who trust ProofLink.AI
          </p>
          <Link href="/auth/register" className="btn btn-primary text-lg px-8 py-4">
            Get Started Free
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Shield className="h-6 w-6" />
                <span className="text-xl font-bold">ProofLink.AI</span>
              </div>
              <p className="text-gray-400">
                The World's Trust Layer
              </p>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="#features">Features</Link></li>
                <li><Link href="#pricing">Pricing</Link></li>
                <li><Link href="/docs">Documentation</Link></li>
                <li><Link href="/api">API</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/about">About</Link></li>
                <li><Link href="/blog">Blog</Link></li>
                <li><Link href="/contact">Contact</Link></li>
                <li><Link href="/careers">Careers</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/privacy">Privacy</Link></li>
                <li><Link href="/terms">Terms</Link></li>
                <li><Link href="/security">Security</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
            <p>&copy; 2025 iTechSmart Inc. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}