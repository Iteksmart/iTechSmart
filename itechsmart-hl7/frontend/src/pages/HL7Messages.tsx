import { useState } from 'react'
import { FileText, Filter } from 'lucide-react'
import { useWebSocket } from '../lib/websocket'

export default function HL7Messages() {
  const [filter, setFilter] = useState('all')
  const { messages } = useWebSocket('hl7')

  const hl7Messages = messages.filter((msg: any) => msg.type === 'hl7_message')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            HL7 Messages
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Real-time HL7 v2.x message monitoring
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Filter className="h-5 w-5 text-gray-400" />
          <select
            className="input w-auto"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">All Messages</option>
            <option value="ADT">ADT Messages</option>
            <option value="ORU">ORU Messages</option>
            <option value="ORM">ORM Messages</option>
          </select>
        </div>
      </div>

      {/* Messages List */}
      <div className="space-y-4">
        {hl7Messages.length > 0 ? (
          hl7Messages.map((message: any, index: number) => (
            <div key={index} className="card p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center">
                    <FileText className="h-5 w-5 text-primary-600 mr-2" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                      {message.data?.message_type || 'HL7 Message'}
                    </h3>
                    <span className="ml-3 badge badge-info">
                      {message.data?.direction || 'inbound'}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    {new Date(message.timestamp || '').toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="mt-4">
                <pre className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg text-xs overflow-x-auto">
                  {JSON.stringify(message.data, null, 2)}
                </pre>
              </div>
            </div>
          ))
        ) : (
          <div className="card p-12 text-center">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              No HL7 messages received yet. Messages will appear here in real-time.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}