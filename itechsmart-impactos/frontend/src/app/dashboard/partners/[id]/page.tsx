'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { ArrowLeft, Star, MapPin, Briefcase, Mail, Phone, Globe, Users } from 'lucide-react';

interface PartnerProfileProps {
  params: { id: string };
}

export default function PartnerProfilePage({ params }: PartnerProfileProps) {
  const { data: partner, isLoading } = useQuery({
    queryKey: ['partner', params.id],
    queryFn: async () => {
      return {
        id: params.id,
        name: 'Tech for Good Foundation',
        type: 'Technology Partner',
        category: 'Technology',
        location: 'San Francisco, CA',
        description: 'We provide technology solutions and consulting services for nonprofits to maximize their impact.',
        rating: 4.8,
        partnerships_count: 45,
        verified: true,
        email: 'contact@techforgood.org',
        phone: '(555) 123-4567',
        website: 'https://techforgood.org',
        services: ['Software Development', 'IT Consulting', 'Cloud Solutions', 'Data Analytics'],
        expertise: ['Healthcare Tech', 'Education Platforms', 'Community Engagement']
      };
    }
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!partner) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/partners" className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-3xl font-bold text-gray-900">{partner.name}</h1>
              {partner.verified && <Star className="w-6 h-6 text-yellow-500 fill-current" />}
            </div>
            <p className="mt-1 text-sm text-gray-500">{partner.type}</p>
          </div>
        </div>
        <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          <Users className="w-4 h-4 mr-2" />
          Request Partnership
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">About</h2>
            <p className="text-gray-700 leading-relaxed">{partner.description}</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Services</h2>
            <div className="flex flex-wrap gap-2">
              {partner.services.map((service, index) => (
                <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                  {service}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Areas of Expertise</h2>
            <div className="flex flex-wrap gap-2">
              {partner.expertise.map((area, index) => (
                <span key={index} className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                  {area}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h2>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <Mail className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Email</p>
                  <a href={`mailto:${partner.email}`} className="text-sm text-blue-600 hover:underline">
                    {partner.email}
                  </a>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <Phone className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Phone</p>
                  <a href={`tel:${partner.phone}`} className="text-sm text-blue-600 hover:underline">
                    {partner.phone}
                  </a>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <Globe className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Website</p>
                  <a href={partner.website} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline">
                    {partner.website}
                  </a>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Location</p>
                  <p className="text-sm text-gray-900">{partner.location}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Statistics</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Rating</span>
                <div className="flex items-center">
                  <Star className="w-4 h-4 text-yellow-500 fill-current mr-1" />
                  <span className="text-sm font-medium text-gray-900">{partner.rating}</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Partnerships</span>
                <span className="text-sm font-medium text-gray-900">{partner.partnerships_count}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}