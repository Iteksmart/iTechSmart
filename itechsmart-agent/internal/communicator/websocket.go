package communicator

import (
	"context"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"

	"github.com/gorilla/websocket"
	"github.com/iteksmart/itechsmart-agent/internal/config"
	"github.com/iteksmart/itechsmart-agent/internal/logger"
)

// Message types
const (
	MessageTypeMetrics       = "metrics"
	MessageTypeCommand       = "command"
	MessageTypeCommandResult = "command_result"
	MessageTypeHeartbeat     = "heartbeat"
	MessageTypeRegister      = "register"
	MessageTypeAlert         = "alert"
	MessageTypeLog           = "log"
)

// Message represents a WebSocket message
type Message struct {
	Type      string                 `json:"type"`
	Timestamp time.Time              `json:"timestamp"`
	AgentID   string                 `json:"agent_id"`
	Payload   map[string]interface{} `json:"payload"`
}

// Command represents a command from the server
type Command struct {
	ID        string                 `json:"id"`
	Type      string                 `json:"type"`
	Timestamp time.Time              `json:"timestamp"`
	Payload   map[string]interface{} `json:"payload"`
}

// CommandResult represents the result of a command execution
type CommandResult struct {
	CommandID string                 `json:"command_id"`
	Success   bool                   `json:"success"`
	Output    string                 `json:"output"`
	Error     string                 `json:"error"`
	Timestamp time.Time              `json:"timestamp"`
	Payload   map[string]interface{} `json:"payload"`
}

// Communicator handles WebSocket communication with the server
type Communicator struct {
	cfg           *config.Config
	log           *logger.Logger
	conn          *websocket.Conn
	mu            sync.RWMutex
	connected     bool
	reconnecting  bool
	commandChan   chan Command
	ctx           context.Context
	cancel        context.CancelFunc
}

// NewCommunicator creates a new communicator
func NewCommunicator(cfg *config.Config, log *logger.Logger) *Communicator {
	ctx, cancel := context.WithCancel(context.Background())
	
	return &Communicator{
		cfg:         cfg,
		log:         log,
		commandChan: make(chan Command, 100),
		ctx:         ctx,
		cancel:      cancel,
	}
}

// Start starts the communicator
func (c *Communicator) Start() error {
	c.log.Info("Starting communicator")
	
	// Initial connection
	if err := c.connect(); err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	
	// Start message handlers
	go c.readMessages()
	go c.heartbeat()
	go c.reconnectLoop()
	
	return nil
}

// Stop stops the communicator
func (c *Communicator) Stop() error {
	c.log.Info("Stopping communicator")
	
	c.cancel()
	
	c.mu.Lock()
	defer c.mu.Unlock()
	
	if c.conn != nil {
		c.conn.WriteMessage(websocket.CloseMessage, websocket.FormatCloseMessage(websocket.CloseNormalClosure, ""))
		c.conn.Close()
		c.conn = nil
	}
	
	close(c.commandChan)
	c.connected = false
	
	return nil
}

// connect establishes WebSocket connection
func (c *Communicator) connect() error {
	c.log.Info("Connecting to server", "url", c.cfg.WebSocketURL)
	
	// Configure TLS
	tlsConfig := &tls.Config{
		MinVersion: tls.VersionTLS13,
	}
	
	if !c.cfg.TLSEnabled {
		tlsConfig.InsecureSkipVerify = true
	}
	
	// Configure dialer
	dialer := websocket.Dialer{
		HandshakeTimeout: 10 * time.Second,
		TLSClientConfig:  tlsConfig,
	}
	
	// Set headers
	headers := http.Header{}
	headers.Set("Authorization", fmt.Sprintf("Bearer %s", c.cfg.APIKey))
	headers.Set("X-Agent-ID", c.cfg.AgentID)
	headers.Set("X-Agent-Version", "1.0.0")
	
	// Connect
	conn, resp, err := dialer.Dial(c.cfg.WebSocketURL, headers)
	if err != nil {
		if resp != nil {
			c.log.Error("Connection failed", "status", resp.Status, "error", err)
		}
		return fmt.Errorf("failed to dial: %w", err)
	}
	
	c.mu.Lock()
	c.conn = conn
	c.connected = true
	c.mu.Unlock()
	
	c.log.Info("Connected to server successfully")
	
	// Send registration message
	if err := c.sendRegistration(); err != nil {
		c.log.Error("Failed to send registration", "error", err)
	}
	
	return nil
}

// sendRegistration sends agent registration message
func (c *Communicator) sendRegistration() error {
	msg := Message{
		Type:      MessageTypeRegister,
		Timestamp: time.Now(),
		AgentID:   c.cfg.AgentID,
		Payload: map[string]interface{}{
			"agent_name":    c.cfg.AgentName,
			"organization":  c.cfg.Organization,
			"platform":      c.cfg.Platform,
			"architecture":  c.cfg.Architecture,
			"version":       "1.0.0",
			"capabilities": []string{
				"system_monitoring",
				"security_checks",
				"software_inventory",
				"remote_commands",
				"patch_management",
			},
		},
	}
	
	return c.SendMessage(msg)
}

// SendMessage sends a message to the server
func (c *Communicator) SendMessage(msg Message) error {
	c.mu.RLock()
	defer c.mu.RUnlock()
	
	if !c.connected || c.conn == nil {
		return fmt.Errorf("not connected")
	}
	
	msg.Timestamp = time.Now()
	msg.AgentID = c.cfg.AgentID
	
	data, err := json.Marshal(msg)
	if err != nil {
		return fmt.Errorf("failed to marshal message: %w", err)
	}
	
	if err := c.conn.WriteMessage(websocket.TextMessage, data); err != nil {
		c.log.Error("Failed to send message", "error", err)
		c.handleDisconnect()
		return fmt.Errorf("failed to write message: %w", err)
	}
	
	return nil
}

// SendMetrics sends metrics to the server
func (c *Communicator) SendMetrics(metricsType string, data interface{}) error {
	payload := map[string]interface{}{
		"metrics_type": metricsType,
		"data":         data,
	}
	
	msg := Message{
		Type:    MessageTypeMetrics,
		Payload: payload,
	}
	
	return c.SendMessage(msg)
}

// SendCommandResult sends command execution result
func (c *Communicator) SendCommandResult(result CommandResult) error {
	payload := map[string]interface{}{
		"command_id": result.CommandID,
		"success":    result.Success,
		"output":     result.Output,
		"error":      result.Error,
		"timestamp":  result.Timestamp,
		"payload":    result.Payload,
	}
	
	msg := Message{
		Type:    MessageTypeCommandResult,
		Payload: payload,
	}
	
	return c.SendMessage(msg)
}

// SendAlert sends an alert to the server
func (c *Communicator) SendAlert(severity, title, description string, metadata map[string]interface{}) error {
	payload := map[string]interface{}{
		"severity":    severity,
		"title":       title,
		"description": description,
		"metadata":    metadata,
	}
	
	msg := Message{
		Type:    MessageTypeAlert,
		Payload: payload,
	}
	
	return c.SendMessage(msg)
}

// readMessages reads messages from the WebSocket
func (c *Communicator) readMessages() {
	for {
		select {
		case <-c.ctx.Done():
			return
		default:
			c.mu.RLock()
			conn := c.conn
			c.mu.RUnlock()
			
			if conn == nil {
				time.Sleep(time.Second)
				continue
			}
			
			_, data, err := conn.ReadMessage()
			if err != nil {
				c.log.Error("Error reading message", "error", err)
				c.handleDisconnect()
				continue
			}
			
			var msg Message
			if err := json.Unmarshal(data, &msg); err != nil {
				c.log.Error("Error unmarshaling message", "error", err)
				continue
			}
			
			c.handleMessage(msg)
		}
	}
}

// handleMessage handles incoming messages
func (c *Communicator) handleMessage(msg Message) {
	c.log.Debug("Received message", "type", msg.Type)
	
	switch msg.Type {
	case MessageTypeCommand:
		c.handleCommand(msg)
	case MessageTypeHeartbeat:
		// Server heartbeat - no action needed
	default:
		c.log.Warn("Unknown message type", "type", msg.Type)
	}
}

// handleCommand handles incoming commands
func (c *Communicator) handleCommand(msg Message) {
	cmd := Command{
		Type:      msg.Payload["command_type"].(string),
		Timestamp: time.Now(),
		Payload:   msg.Payload,
	}
	
	if id, ok := msg.Payload["command_id"].(string); ok {
		cmd.ID = id
	}
	
	select {
	case c.commandChan <- cmd:
		c.log.Info("Command queued", "type", cmd.Type, "id", cmd.ID)
	default:
		c.log.Warn("Command channel full, dropping command", "type", cmd.Type)
	}
}

// GetCommandChannel returns the command channel
func (c *Communicator) GetCommandChannel() <-chan Command {
	return c.commandChan
}

// heartbeat sends periodic heartbeat messages
func (c *Communicator) heartbeat() {
	ticker := time.NewTicker(time.Duration(c.cfg.HeartbeatInterval) * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-c.ctx.Done():
			return
		case <-ticker.C:
			if c.IsConnected() {
				msg := Message{
					Type: MessageTypeHeartbeat,
					Payload: map[string]interface{}{
						"status": "alive",
					},
				}
				
				if err := c.SendMessage(msg); err != nil {
					c.log.Error("Failed to send heartbeat", "error", err)
				}
			}
		}
	}
}

// reconnectLoop handles automatic reconnection
func (c *Communicator) reconnectLoop() {
	ticker := time.NewTicker(time.Duration(c.cfg.ReconnectInterval) * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-c.ctx.Done():
			return
		case <-ticker.C:
			if !c.IsConnected() && !c.reconnecting {
				c.reconnecting = true
				c.log.Info("Attempting to reconnect...")
				
				if err := c.connect(); err != nil {
					c.log.Error("Reconnection failed", "error", err)
				} else {
					c.log.Info("Reconnected successfully")
					go c.readMessages()
				}
				
				c.reconnecting = false
			}
		}
	}
}

// handleDisconnect handles disconnection
func (c *Communicator) handleDisconnect() {
	c.mu.Lock()
	defer c.mu.Unlock()
	
	if c.conn != nil {
		c.conn.Close()
		c.conn = nil
	}
	
	c.connected = false
	c.log.Warn("Disconnected from server")
}

// IsConnected returns connection status
func (c *Communicator) IsConnected() bool {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.connected
}