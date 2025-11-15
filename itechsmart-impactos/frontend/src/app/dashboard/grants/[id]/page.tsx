'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { 
  ArrowLeft, 
  FileText, 
  DollarSign,
  Calendar,
  Users,
  ExternalLink,
  Bookmark,
  CheckCircle,
  AlertCircle,
  Download
} from 'lucide-react';

interface GrantDetailsProps {
  params: {
    id: string;
  };
}

export default function GrantDetailsPage({ params }: GrantDetailsProps) {
  const { data: grant, isLoading } = useQuery({
    queryKey: ['grant', params.id],
    queryFn: async () => {
      return {
        id: params.id,
        title: 'Community Health Innovation Grant',
        funder: 'National Health Foundation',
        amount_min: 50000,
        amount_max: 250000,
        deadline: '2024-06-30',
        category: 'Healthcare',
        status: 'open',
        match_score: 92,
        saved: true,
        description: 'The Community Health Innovation Grant supports nonprofit organizations developing innovative approaches to improving health outcomes in underserved communities. This grant prioritizes projects that address health disparities, promote preventive care, and leverage technology to expand access to healthcare services.',
        eligibility: [
          '501(c)(3) nonprofit organizations',
          'Minimum 3 years of operational history',
          'Serving communities with documented health disparities',
          'Annual budget between $500,000 and $5,000,000',
          'Located in the United States'
        ],
        requirements: [
          'Detailed project proposal (10-15 pages)',
          'Organizational budget for current and previous fiscal year',
          'IRS determination letter',
          'Board of Directors list',
          'Letters of support from community partners',
          'Logic model or theory of change',
          'Evaluation plan with measurable outcomes'
        ],
        timeline: [
          { date: '2024-04-01', event: 'Application Opens', status: 'completed' },
          { date: '2024-05-15', event: 'Letter of Intent Due', status: 'upcoming' },
          { date: '2024-06-30', event: 'Full Proposal Due', status: 'upcoming' },
          { date: '2024-08-15', event: 'Finalists Notified', status: 'upcoming' },
          { date: '2024-09-30', event: 'Awards Announced', status: 'upcoming' }
        ],
        contact: {
          name: 'Dr. Sarah Johnson',
          title: 'Program Director',
          email: 'sjohnson@nhf.org',
          phone: '(555) 123-4567'
        },
        website: 'https://www.nhf.org/grants/community-health-innovation'
      };
    }
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-500">Loading grant details...</p>
        </div>
      </div>
    );
  }

  if (!grant) {
    return (
      <div className="text-center py-12">
        <FileText className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Grant not found</h3>
        <p className="mt-1 text-sm text-gray-500">
          The grant you're looking for doesn't exist.
        </p>
        <div className="mt-6">
          <Link
            href="/dashboard/grants"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Grants
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            href="/dashboard/grants"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-3xl font-bold text-gray-900">{grant.title}</h1>
              {grant.saved && (
                <Bookmark className="w-6 h-6 text-yellow-500 fill-current" />
              )}
            </div>
            <p className="mt-1 text-sm text-gray-500">{grant.funder}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {!grant.saved && (
            <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <Bookmark className="w-4 h-4 mr-2" />
              Save Grant
            </button>
          )}
          <Link
            href={`/dashboard/proposals/new?grant=${params.id}`}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <FileText className="w-4 h-4 mr-2" />
            Start Proposal
          </Link>
        </div>
      </div>

      {/* Key Information */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="w-8 h-8 text-green-600" />
          </div>
          <p className="text-sm text-gray-500">Award Range</p>
          <p className="text-lg font-bold text-gray-900 mt-1">
            {formatCurrency(grant.amount_min)} - {formatCurrency(grant.amount_max)}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <Calendar className="w-8 h-8 text-blue-600" />
          </div>
          <p className="text-sm text-gray-500">Deadline</p>
          <p className="text-lg font-bold text-gray-900 mt-1">
            {formatDate(grant.deadline)}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <FileText className="w-8 h-8 text-purple-600" />
          </div>
          <p className="text-sm text-gray-500">Category</p>
          <p className="text-lg font-bold text-gray-900 mt-1">{grant.category}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <CheckCircle className="w-8 h-8 text-orange-600" />
          </div>
          <p className="text-sm text-gray-500">Match Score</p>
          <p className="text-lg font-bold text-gray-900 mt-1">{grant.match_score}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Grant Description</h2>
            <p className="text-gray-700 leading-relaxed">{grant.description}</p>
          </div>

          {/* Eligibility */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Eligibility Requirements</h2>
            <ul className="space-y-3">
              {grant.eligibility.map((item, index) => (
                <li key={index} className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Requirements */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Application Requirements</h2>
            <ul className="space-y-3">
              {grant.requirements.map((item, index) => (
                <li key={index} className="flex items-start space-x-3">
                  <FileText className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Timeline */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Application Timeline</h2>
            <div className="space-y-4">
              {grant.timeline.map((item, index) => (
                <div key={index} className="flex items-start space-x-4">
                  <div className={`p-2 rounded-lg ${
                    item.status === 'completed' ? 'bg-green-100' : 'bg-blue-100'
                  }`}>
                    {item.status === 'completed' ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <Calendar className="w-5 h-5 text-blue-600" />
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{item.event}</p>
                    <p className="text-sm text-gray-500">{formatDate(item.date)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Contact Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-900">{grant.contact.name}</p>
                <p className="text-sm text-gray-500">{grant.contact.title}</p>
              </div>
              <div className="space-y-2">
                <a 
                  href={`mailto:${grant.contact.email}`}
                  className="flex items-center space-x-2 text-sm text-blue-600 hover:underline"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>{grant.contact.email}</span>
                </a>
                <a 
                  href={`tel:${grant.contact.phone}`}
                  className="flex items-center space-x-2 text-sm text-blue-600 hover:underline"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>{grant.contact.phone}</span>
                </a>
              </div>
            </div>
          </div>

          {/* Resources */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Resources</h2>
            <div className="space-y-2">
              <a
                href={grant.website}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <span className="text-sm text-gray-900">Grant Website</span>
                <ExternalLink className="w-4 h-4 text-gray-400" />
              </a>
              <button className="w-full flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <span className="text-sm text-gray-900">Application Guidelines</span>
                <Download className="w-4 h-4 text-gray-400" />
              </button>
              <button className="w-full flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <span className="text-sm text-gray-900">Sample Proposal</span>
                <Download className="w-4 h-4 text-gray-400" />
              </button>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <Link
                href={`/dashboard/proposals/new?grant=${params.id}`}
                className="block w-full px-4 py-2 text-sm text-center bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Start Proposal
              </Link>
              <button className="block w-full px-4 py-2 text-sm text-center border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                Share Grant
              </button>
              <button className="block w-full px-4 py-2 text-sm text-center border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                Set Reminder
              </button>
            </div>
          </div>

          {/* Match Analysis */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Match Analysis</h2>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Overall Match</span>
                  <span className="text-sm font-bold text-gray-900">{grant.match_score}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${grant.match_score}%` }}
                  ></div>
                </div>
              </div>
              <div className="pt-4 border-t border-gray-200">
                <p className="text-xs text-gray-500 mb-2">Why this is a good match:</p>
                <ul className="space-y-2">
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5" />
                    <span className="text-xs text-gray-700">Category aligns with your focus area</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5" />
                    <span className="text-xs text-gray-700">Budget range matches your capacity</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5" />
                    <span className="text-xs text-gray-700">You meet all eligibility criteria</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}