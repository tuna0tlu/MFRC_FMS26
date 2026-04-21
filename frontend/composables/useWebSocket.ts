import { ref } from 'vue'

export const useWebSocket = () => {
  const isConnecting = ref(true)
  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let shouldReconnect = false

  const connect = (url: string, onMessage: (data: any) => void) => {
    shouldReconnect = true

    const openSocket = () => {
      if (!shouldReconnect) return

      ws = new WebSocket(url)

      ws.onopen = () => {
        console.log("Connected to the server")
        isConnecting.value = false
      }

      ws.onerror = (error) => {
        console.error("WebSocket error:", error)
      }

      ws.onmessage = (event) => {
        console.log("New message from server: ", event.data)
        const data = JSON.parse(event.data)
        onMessage(data)
      }

      ws.onclose = () => {
        ws = null
        if (!shouldReconnect) return

        console.log("Disconnected from the server. Reconnecting...")
        isConnecting.value = true
        reconnectTimer = setTimeout(() => openSocket(), 1000) // Retry connection after 1 second
      }
    }

    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      ws.close()
    }

    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    openSocket()
  }

  const disconnect = () => {
    shouldReconnect = false

    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      ws.close()
    }
    ws = null
    isConnecting.value = true
  }

  return {
    isReconnecting: isConnecting,
    connect,
    disconnect
  }
}
