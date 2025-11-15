import { useEffect, useState, useRef } from 'react'

const WS_BASE_URL = (import.meta as any).env?.VITE_WS_URL || 'ws://localhost:8000'

interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

interface UseWebSocketReturn {
  isConnected: boolean
  lastMessage: WebSocketMessage | null
  messages: WebSocketMessage[]
  sendMessage: (message: any) => void
  error: Error | null
}

export function useWebSocket(channel: string = 'default'): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [messages, setMessages] = useState<WebSocketMessage[]>([])
  const [error, setError] = useState<Error | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>()

  const connect = () => {
    try {
      const token = localStorage.getItem('token')
      const wsUrl = `${WS_BASE_URL}/ws/${channel}${token ? `?token=${token}` : ''}`
      
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log(`WebSocket connected to channel: ${channel}`)
        setIsConnected(true)
        setError(null)
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          setLastMessage(message)
          setMessages(prev => [...prev, message])
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }

      ws.onerror = (event) => {
        console.error('WebSocket error:', event)
        setError(new Error('WebSocket connection error'))
      }

      ws.onclose = () => {
        console.log(`WebSocket disconnected from channel: ${channel}`)
        setIsConnected(false)
        
        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...')
          connect()
        }, 3000)
      }
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err)
      setError(err as Error)
    }
  }

  useEffect(() => {
    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [channel])

  const sendMessage = (message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.error('WebSocket is not connected')
    }
  }

  return {
    isConnected,
    lastMessage,
    messages,
    sendMessage,
    error,
  }
}

export default useWebSocket