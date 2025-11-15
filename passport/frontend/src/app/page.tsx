'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  Shield,
  Lock,
  Smartphone,
  Zap,
  Globe,
  Key,
  CheckCircle,
  ArrowRight,
  Star,
  Users,
  Fingerprint,
  Cloud,
  AlertTriangle,
  RefreshCw,
  Eye,
  Sparkles,
} from 'lucide-react';

export default function LandingPage() {
  const features = [
    {
      icon: Lock,
      title: 'One PassPhrase',
      description: 'Remember just one passphrase. We handle the rest.',
      color: 'blue',
    },
    {
      icon: Fingerprint,
      title: 'Biometric Login',
      description: 'Face ID, Touch ID, or fingerprint authentication.',
      color: 'purple',
    },
    {
      icon: Shield,
      title: 'Military-Grade Security',
      description: 'AES-256 encryption with hardware secure enclave.',
      color: 'green',
    },
    {
      icon: Zap,
      title: 'Instant Auto-Fill',
      description: 'Login to any app or website in milliseconds.',
      color: 'yellow',
    },
    {
      icon: Globe,
      title: 'Works Everywhere',
      description: 'Phone, tablet, desktop, and web - all synced.',
      color: 'indigo',
    },
    {
      icon: RefreshCw,
      title: 'Auto Password Rotation',
      description: 'AI detects weak passwords and fixes them automatically.',
      color: 'red',
    },
  ];

  const problems = [
    'Forgetting passwords constantly',
    'Using the same password everywhere',
    'Losing access to important accounts',
    'Paying $50+/year for password managers',
    'Struggling with 2FA codes',
    'Getting locked out of accounts',
  ];

  const useCases = [
    {
      icon: Smartphone,
      title: 'Forgot Your Password?',
      description: '"Hey PassPort, log me into Netflix."',
      color: 'blue',
    },
    {
      icon: Key,
      title: 'Buying Online?',
      description: 'Autofill + 2FA instantly.',
      color: 'green',
    },
    {
      icon: Cloud,
      title: 'Switching Devices?',
      description: 'Scan QR → everything restored.',
      color: 'purple',
    },
    {
      icon: AlertTriangle,
      title: 'Password Leak Detected?',
      description: 'AI rotates passwords automatically.',
      color: 'red',
    },
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Small Business Owner',
      avatar: '👩‍💼',
      text: 'I used to spend hours resetting passwords. PassPort saved my sanity and my business.',
      rating: 5,
    },
    {
      name: 'Marcus Johnson',
      role: 'Software Engineer',
      avatar: '👨‍💻',
      text: 'Finally, a password manager that actually works the way I think. The AI is incredible.',
      rating: 5,
    },
    {
      name: 'Emily Rodriguez',
      role: 'Teacher',
      avatar: '👩‍🏫',
      text: 'For just $1, this is the best tech purchase I\'ve ever made. My whole family uses it.',
      rating: 5,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-black bg-opacity-50 backdrop-blur-lg z-50 border-b border-white border-opacity-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">iTechSmart PassPort</h1>
                <p className="text-xs text-blue-300">Your Last Password, Forever</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/auth/login"
                className="text-white hover:text-blue-300 transition-colors"
              >
                Login
              </Link>
              <Link
                href="/auth/register"
                className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 bg-opacity-20 rounded-full border border-blue-400 border-opacity-30 mb-6">
              <Sparkles className="w-4 h-4 text-blue-300" />
              <span className="text-blue-200 text-sm font-medium">
                The One Login for Your Entire Life
              </span>
            </div>

            <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight">
              Never Forget a Password
              <br />
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Ever Again
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-blue-200 mb-8 max-w-3xl mx-auto">
              Just $1 to own your digital identity. One PassPhrase. Infinite peace of mind.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link
                href="/auth/register"
                className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all text-lg font-semibold flex items-center justify-center gap-2 shadow-2xl"
              >
                Get PassPort for $1
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="#how-it-works"
                className="px-8 py-4 bg-white bg-opacity-10 text-white rounded-xl hover:bg-opacity-20 transition-all text-lg font-semibold backdrop-blur-sm border border-white border-opacity-20"
              >
                See How It Works
              </Link>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-wrap items-center justify-center gap-8 text-blue-200">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-green-400" />
                <span>Military-Grade Encryption</span>
              </div>
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-400" />
                <span>10,000+ Users</span>
              </div>
              <div className="flex items-center gap-2">
                <Star className="w-5 h-5 text-yellow-400" />
                <span>4.9/5 Rating</span>
              </div>
            </div>
          </motion.div>

          {/* Hero Image/Demo */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mt-16"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl blur-3xl opacity-30"></div>
              <div className="relative bg-gradient-to-br from-slate-800 to-slate-900 rounded-3xl p-8 border border-white border-opacity-10 shadow-2xl">
                <div className="aspect-video bg-gradient-to-br from-blue-900 to-purple-900 rounded-xl flex items-center justify-center">
                  <div className="text-center">
                    <Lock className="w-20 h-20 text-blue-300 mx-auto mb-4" />
                    <p className="text-white text-xl font-semibold">Your Digital Vault</p>
                    <p className="text-blue-300">Secure. Simple. Powerful.</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-20 px-6 bg-black bg-opacity-30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Everyone's Drowning in Passwords
            </h2>
            <p className="text-xl text-blue-200">
              The average person has 100+ online accounts. That's 100+ passwords to remember.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {problems.map((problem, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-gradient-to-br from-red-900 to-red-800 bg-opacity-30 rounded-xl p-6 border border-red-500 border-opacity-30"
              >
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-6 h-6 text-red-400 flex-shrink-0 mt-1" />
                  <p className="text-white text-lg">{problem}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              One PassPhrase. Infinite Possibilities.
            </h2>
            <p className="text-xl text-blue-200">
              PassPort.AI manages everything so you don't have to.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              const colorClasses = {
                blue: 'from-blue-500 to-blue-600',
                purple: 'from-purple-500 to-purple-600',
                green: 'from-green-500 to-green-600',
                yellow: 'from-yellow-500 to-orange-600',
                indigo: 'from-indigo-500 to-indigo-600',
                red: 'from-red-500 to-red-600',
              };

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-8 border border-white border-opacity-10 hover:border-opacity-30 transition-all group"
                >
                  <div
                    className={`w-14 h-14 bg-gradient-to-br ${
                      colorClasses[feature.color as keyof typeof colorClasses]
                    } rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}
                  >
                    <Icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-3">{feature.title}</h3>
                  <p className="text-blue-200 text-lg">{feature.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section id="how-it-works" className="py-20 px-6 bg-black bg-opacity-30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              How PassPort Works in Real Life
            </h2>
            <p className="text-xl text-blue-200">
              See how PassPort solves everyday problems instantly.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {useCases.map((useCase, index) => {
              const Icon = useCase.icon;
              const colorClasses = {
                blue: 'from-blue-500 to-blue-600',
                green: 'from-green-500 to-green-600',
                purple: 'from-purple-500 to-purple-600',
                red: 'from-red-500 to-red-600',
              };

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-8 border border-white border-opacity-10"
                >
                  <div
                    className={`w-16 h-16 bg-gradient-to-br ${
                      colorClasses[useCase.color as keyof typeof colorClasses]
                    } rounded-xl flex items-center justify-center mb-6`}
                  >
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-3">{useCase.title}</h3>
                  <p className="text-blue-200 text-xl italic">"{useCase.description}"</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Simple, Honest Pricing
            </h2>
            <p className="text-xl text-blue-200">
              No subscriptions. No hidden fees. Just $1.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Personal */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-8 border border-white border-opacity-10">
              <h3 className="text-2xl font-bold text-white mb-2">Personal</h3>
              <div className="mb-6">
                <span className="text-5xl font-bold text-white">$1</span>
                <span className="text-blue-200 ml-2">lifetime</span>
              </div>
              <ul className="space-y-3 mb-8">
                {['Unlimited passwords', 'All devices', 'Biometric auth', '2FA storage', 'Auto-fill'].map(
                  (feature, i) => (
                    <li key={i} className="flex items-center text-blue-200">
                      <CheckCircle className="w-5 h-5 text-green-400 mr-3" />
                      {feature}
                    </li>
                  )
                )}
              </ul>
              <Link
                href="/auth/register"
                className="block w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all text-center font-semibold"
              >
                Get Started
              </Link>
            </div>

            {/* Family - Featured */}
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl p-8 border-2 border-yellow-400 relative transform scale-105">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 px-4 py-1 bg-yellow-400 text-black rounded-full text-sm font-bold">
                BEST VALUE
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Family</h3>
              <div className="mb-6">
                <span className="text-5xl font-bold text-white">$1</span>
                <span className="text-blue-100 ml-2">for 5 users</span>
              </div>
              <ul className="space-y-3 mb-8">
                {[
                  'Everything in Personal',
                  'Up to 5 family members',
                  'Shared vaults',
                  'Emergency access',
                  'Priority support',
                ].map((feature, i) => (
                  <li key={i} className="flex items-center text-white">
                    <CheckCircle className="w-5 h-5 text-yellow-300 mr-3" />
                    {feature}
                  </li>
                ))}
              </ul>
              <Link
                href="/auth/register?plan=family"
                className="block w-full px-6 py-3 bg-white text-purple-600 rounded-xl hover:bg-blue-50 transition-all text-center font-semibold"
              >
                Get Family Plan
              </Link>
            </div>

            {/* Pro */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-8 border border-white border-opacity-10">
              <h3 className="text-2xl font-bold text-white mb-2">Pro</h3>
              <div className="mb-6">
                <span className="text-5xl font-bold text-white">$3</span>
                <span className="text-blue-200 ml-2">/month</span>
              </div>
              <ul className="space-y-3 mb-8">
                {[
                  'Everything in Family',
                  'Team credential sharing',
                  'Admin controls',
                  'Audit logs',
                  'API access',
                ].map((feature, i) => (
                  <li key={i} className="flex items-center text-blue-200">
                    <CheckCircle className="w-5 h-5 text-green-400 mr-3" />
                    {feature}
                  </li>
                ))}
              </ul>
              <Link
                href="/auth/register?plan=pro"
                className="block w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all text-center font-semibold"
              >
                Get Pro
              </Link>
            </div>
          </div>

          {/* Nonprofit Note */}
          <div className="mt-12 text-center">
            <p className="text-blue-200 text-lg">
              <span className="font-semibold text-white">Free for nonprofits and schools</span> —
              part of iTechSmart's CSR mission
            </p>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-6 bg-black bg-opacity-30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Loved by Thousands
            </h2>
            <p className="text-xl text-blue-200">
              See what people are saying about PassPort.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-8 border border-white border-opacity-10"
              >
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                  ))}
                </div>
                <p className="text-blue-100 text-lg mb-6 italic">"{testimonial.text}"</p>
                <div className="flex items-center gap-3">
                  <div className="text-4xl">{testimonial.avatar}</div>
                  <div>
                    <p className="text-white font-semibold">{testimonial.name}</p>
                    <p className="text-blue-300 text-sm">{testimonial.role}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Security Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gradient-to-br from-green-900 to-emerald-900 rounded-3xl p-12 border border-green-500 border-opacity-30">
            <div className="text-center mb-12">
              <Shield className="w-20 h-20 text-green-400 mx-auto mb-6" />
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                Bank-Level Security
              </h2>
              <p className="text-xl text-green-200">
                Your passwords are safer with PassPort than anywhere else.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { icon: Lock, title: 'AES-256 Encryption', desc: 'Military-grade security' },
                { icon: Eye, title: 'Zero-Knowledge', desc: 'We never see your data' },
                { icon: Shield, title: 'Secure Enclave', desc: 'Hardware-based protection' },
                { icon: CheckCircle, title: 'Audit Logs', desc: 'Track every access' },
              ].map((item, index) => {
                const Icon = item.icon;
                return (
                  <div key={index} className="text-center">
                    <div className="w-16 h-16 bg-green-500 bg-opacity-20 rounded-xl flex items-center justify-center mx-auto mb-4">
                      <Icon className="w-8 h-8 text-green-400" />
                    </div>
                    <h3 className="text-white font-bold mb-2">{item.title}</h3>
                    <p className="text-green-200 text-sm">{item.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
          >
            <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Your Last Password,
              <br />
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Forever
              </span>
            </h2>
            <p className="text-2xl text-blue-200 mb-8">
              $1 to secure your digital life. One PassPhrase. Infinite peace of mind.
            </p>
            <Link
              href="/auth/register"
              className="inline-flex items-center px-12 py-5 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all text-xl font-bold shadow-2xl gap-3"
            >
              Get PassPort Now
              <ArrowRight className="w-6 h-6" />
            </Link>
            <p className="mt-6 text-blue-300">
              Join 10,000+ people who never forget passwords anymore
            </p>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 bg-black bg-opacity-50 border-t border-white border-opacity-10">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <span className="text-white font-bold text-lg">PassPort</span>
              </div>
              <p className="text-blue-300 text-sm">
                Your Last Password, Forever.
              </p>
            </div>

            <div>
              <h3 className="text-white font-semibold mb-4">Product</h3>
              <ul className="space-y-2">
                {['Features', 'Security', 'Pricing', 'Download'].map((item) => (
                  <li key={item}>
                    <a href="#" className="text-blue-300 hover:text-white transition-colors text-sm">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-white font-semibold mb-4">Company</h3>
              <ul className="space-y-2">
                {['About', 'Blog', 'Careers', 'Contact'].map((item) => (
                  <li key={item}>
                    <a href="#" className="text-blue-300 hover:text-white transition-colors text-sm">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-white font-semibold mb-4">Legal</h3>
              <ul className="space-y-2">
                {['Privacy', 'Terms', 'Security', 'Compliance'].map((item) => (
                  <li key={item}>
                    <a href="#" className="text-blue-300 hover:text-white transition-colors text-sm">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-white border-opacity-10 text-center">
            <p className="text-blue-300 text-sm">
              © 2025 iTechSmart Inc. All rights reserved. Built with ❤️ for digital freedom.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}