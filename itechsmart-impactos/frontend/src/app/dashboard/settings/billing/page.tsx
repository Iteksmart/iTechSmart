'use client';

import Link from 'next/link';
import { ArrowLeft, CreditCard, Download } from 'lucide-react';

export default function BillingSettingsPage() {
  const invoices = [
    { date: '2024-04-01', amount: 99, status: 'Paid' },
    { date: '2024-03-01', amount: 99, status: 'Paid' },
    { date: '2024-02-01', amount: 99, status: 'Paid' }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/dashboard/settings" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Billing & Subscription</h1>
          <p className="mt-1 text-sm text-gray-500">Manage your subscription and billing</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Current Plan</h2>
        <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
          <div>
            <p className="text-lg font-semibold text-gray-900">Professional Plan</p>
            <p className="text-sm text-gray-600">$99/month • Billed monthly</p>
          </div>
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-white">
            Change Plan
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Payment Method</h2>
        <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <CreditCard className="w-6 h-6 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900">•••• •••• •••• 4242</p>
              <p className="text-xs text-gray-500">Expires 12/2025</p>
            </div>
          </div>
          <button className="text-sm text-blue-600 hover:text-blue-700">Update</button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Billing History</h2>
        <div className="space-y-3">
          {invoices.map((invoice, index) => (
            <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-900">{invoice.date}</p>
                <p className="text-xs text-gray-500">${invoice.amount}.00</p>
              </div>
              <div className="flex items-center space-x-3">
                <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                  {invoice.status}
                </span>
                <button className="text-sm text-blue-600 hover:text-blue-700">
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}