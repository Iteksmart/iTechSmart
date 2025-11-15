'use client'

import { useQuery } from '@tanstack/react-query'
import DashboardLayout from '@/components/layout/DashboardLayout'
import {
  UserGroupIcon,
  ClipboardDocumentListIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
} from '@heroicons/react/24/outline'
import { authApi } from '@/lib/api'

const stats = [
  {
    name: 'Total Beneficiaries',
    value: '12,543',
    change: '+12.5%',
    changeType: 'positive',
    icon: UserGroupIcon,
  },
  {
    name: 'Active Programs',
    value: '24',
    change: '+3',
    changeType: 'positive',
    icon: ClipboardDocumentListIcon,
  },
  {
    name: 'Total Budget',
    value: '$2.4M',
    change: '+18.2%',
    changeType: 'positive',
    icon: CurrencyDollarIcon,
  },
  {
    name: 'Impact Score',
    value: '87/100',
    change: '+5',
    changeType: 'positive',
    icon: ChartBarIcon,
  },
]

const recentActivity = [
  {
    id: 1,
    type: 'report',
    title: 'Q4 2023 Impact Report Generated',
    description: 'Youth Education Program',
    time: '2 hours ago',
  },
  {
    id: 2,
    type: 'grant',
    title: 'Grant Proposal Submitted',
    description: 'Community Development Grant - $50,000',
    time: '5 hours ago',
  },
  {
    id: 3,
    type: 'program',
    title: 'New Program Created',
    description: 'Senior Wellness Initiative',
    time: '1 day ago',
  },
  {
    id: 4,
    type: 'partner',
    title: 'Partnership Established',
    description: 'Tech for Good Foundation',
    time: '2 days ago',
  },
]

const upcomingDeadlines = [
  {
    id: 1,
    title: 'Education Innovation Fund',
    type: 'Grant Application',
    deadline: '2024-01-30',
    daysLeft: 15,
  },
  {
    id: 2,
    title: 'Q1 2024 Impact Report',
    type: 'Report Due',
    deadline: '2024-02-15',
    daysLeft: 31,
  },
  {
    id: 3,
    title: 'Annual Board Meeting',
    type: 'Meeting',
    deadline: '2024-02-20',
    daysLeft: 36,
  },
]

export default function DashboardPage() {
  const { data: user } = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const response = await authApi.getCurrentUser()
      return response.data
    },
  })

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Welcome Section */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome back, {user?.full_name?.split(' ')[0] || 'User'}!
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Here's what's happening with your impact today.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <div
              key={stat.name}
              className="bg-white dark:bg-gray-800 overflow-hidden rounded-lg shadow hover:shadow-lg transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <stat.icon className="h-8 w-8 text-primary-600" aria-hidden="true" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        {stat.name}
                      </dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900 dark:text-white">
                          {stat.value}
                        </div>
                        <div
                          className={`ml-2 flex items-baseline text-sm font-semibold ${
                            stat.changeType === 'positive'
                              ? 'text-green-600'
                              : 'text-red-600'
                          }`}
                        >
                          {stat.changeType === 'positive' ? (
                            <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                          ) : (
                            <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                          )}
                          {stat.change}
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Recent Activity */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Recent Activity
              </h2>
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                        <span className="text-primary-600 dark:text-primary-400 font-semibold">
                          {activity.type[0].toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {activity.title}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {activity.description}
                      </p>
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                        {activity.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              <button className="mt-4 w-full text-center text-sm text-primary-600 hover:text-primary-700 font-medium">
                View all activity
              </button>
            </div>
          </div>

          {/* Upcoming Deadlines */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Upcoming Deadlines
              </h2>
              <div className="space-y-4">
                {upcomingDeadlines.map((deadline) => (
                  <div
                    key={deadline.id}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {deadline.title}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {deadline.type}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">
                        {deadline.daysLeft} days
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {deadline.deadline}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              <button className="mt-4 w-full text-center text-sm text-primary-600 hover:text-primary-700 font-medium">
                View all deadlines
              </button>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-gradient-to-r from-primary-600 to-purple-600 rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <button className="bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white rounded-lg p-4 text-left transition-colors">
              <ClipboardDocumentListIcon className="h-6 w-6 mb-2" />
              <p className="font-medium">Create Program</p>
            </button>
            <button className="bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white rounded-lg p-4 text-left transition-colors">
              <CurrencyDollarIcon className="h-6 w-6 mb-2" />
              <p className="font-medium">Search Grants</p>
            </button>
            <button className="bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white rounded-lg p-4 text-left transition-colors">
              <ChartBarIcon className="h-6 w-6 mb-2" />
              <p className="font-medium">Generate Report</p>
            </button>
            <button className="bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white rounded-lg p-4 text-left transition-colors">
              <UserGroupIcon className="h-6 w-6 mb-2" />
              <p className="font-medium">Find Partners</p>
            </button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}