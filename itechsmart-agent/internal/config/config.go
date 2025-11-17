package config

import (
	"fmt"
	"os"
	"runtime"

	"github.com/spf13/viper"
)

// Config holds all configuration for the agent
type Config struct {
	// Agent identification
	AgentID      string `mapstructure:"agent_id"`
	AgentName    string `mapstructure:"agent_name"`
	Organization string `mapstructure:"organization"`
	
	// Server configuration
	ServerURL    string `mapstructure:"server_url"`
	APIKey       string `mapstructure:"api_key"`
	APISecret    string `mapstructure:"api_secret"`
	
	// Communication settings
	WebSocketURL      string `mapstructure:"websocket_url"`
	ReconnectInterval int    `mapstructure:"reconnect_interval"` // seconds
	HeartbeatInterval int    `mapstructure:"heartbeat_interval"` // seconds
	
	// Collection intervals (seconds)
	SystemMetricsInterval   int `mapstructure:"system_metrics_interval"`
	ProcessMetricsInterval  int `mapstructure:"process_metrics_interval"`
	NetworkMetricsInterval  int `mapstructure:"network_metrics_interval"`
	SecurityCheckInterval   int `mapstructure:"security_check_interval"`
	SoftwareInventoryInterval int `mapstructure:"software_inventory_interval"`
	
	// Features
	EnableSystemMonitoring   bool `mapstructure:"enable_system_monitoring"`
	EnableSecurityChecks     bool `mapstructure:"enable_security_checks"`
	EnableSoftwareInventory  bool `mapstructure:"enable_software_inventory"`
	EnableRemoteCommands     bool `mapstructure:"enable_remote_commands"`
	EnablePatchManagement    bool `mapstructure:"enable_patch_management"`
	EnableAuditLogging       bool `mapstructure:"enable_audit_logging"`
	
	// Logging
	LogLevel string `mapstructure:"log_level"`
	LogFile  string `mapstructure:"log_file"`
	
	// Platform
	Platform     string `mapstructure:"platform"`
	Architecture string `mapstructure:"architecture"`
	
	// Security
	TLSEnabled         bool   `mapstructure:"tls_enabled"`
	TLSCertFile        string `mapstructure:"tls_cert_file"`
	TLSKeyFile         string `mapstructure:"tls_key_file"`
	TLSCAFile          string `mapstructure:"tls_ca_file"`
	CertificatePinning bool   `mapstructure:"certificate_pinning"`
	
	// Product integration
	NinjaEnabled      bool   `mapstructure:"ninja_enabled"`
	NinjaURL          string `mapstructure:"ninja_url"`
	EnterpriseEnabled bool   `mapstructure:"enterprise_enabled"`
	EnterpriseURL     string `mapstructure:"enterprise_url"`
	
	// Data retention
	MetricsRetentionDays int `mapstructure:"metrics_retention_days"`
	LogsRetentionDays    int `mapstructure:"logs_retention_days"`
}

// Load loads configuration from file or environment variables
func Load(cfgFile string) (*Config, error) {
	v := viper.New()
	
	// Set defaults
	setDefaults(v)
	
	// Config file
	if cfgFile != "" {
		v.SetConfigFile(cfgFile)
	} else {
		// Search for config in standard locations
		v.SetConfigName("agent")
		v.SetConfigType("yaml")
		v.AddConfigPath("/etc/itechsmart/")
		v.AddConfigPath("$HOME/.itechsmart/")
		v.AddConfigPath(".")
	}
	
	// Environment variables
	v.SetEnvPrefix("ITECHSMART")
	v.AutomaticEnv()
	
	// Read config file
	if err := v.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, fmt.Errorf("error reading config file: %w", err)
		}
		// Config file not found; using defaults and env vars
	}
	
	// Unmarshal config
	var cfg Config
	if err := v.Unmarshal(&cfg); err != nil {
		return nil, fmt.Errorf("error unmarshaling config: %w", err)
	}
	
	// Set platform info
	cfg.Platform = runtime.GOOS
	cfg.Architecture = runtime.GOARCH
	
	// Generate agent ID if not set
	if cfg.AgentID == "" {
		hostname, _ := os.Hostname()
		cfg.AgentID = fmt.Sprintf("%s-%s", hostname, generateRandomID())
	}
	
	// Validate configuration
	if err := cfg.Validate(); err != nil {
		return nil, fmt.Errorf("invalid configuration: %w", err)
	}
	
	return &cfg, nil
}

// setDefaults sets default configuration values
func setDefaults(v *viper.Viper) {
	// Server
	v.SetDefault("server_url", "https://api.itechsmart.dev")
	v.SetDefault("websocket_url", "wss://api.itechsmart.dev/agent/ws")
	
	// Intervals (seconds)
	v.SetDefault("reconnect_interval", 30)
	v.SetDefault("heartbeat_interval", 60)
	v.SetDefault("system_metrics_interval", 60)
	v.SetDefault("process_metrics_interval", 300)
	v.SetDefault("network_metrics_interval", 60)
	v.SetDefault("security_check_interval", 3600)
	v.SetDefault("software_inventory_interval", 86400)
	
	// Features
	v.SetDefault("enable_system_monitoring", true)
	v.SetDefault("enable_security_checks", true)
	v.SetDefault("enable_software_inventory", true)
	v.SetDefault("enable_remote_commands", true)
	v.SetDefault("enable_patch_management", true)
	v.SetDefault("enable_audit_logging", true)
	
	// Logging
	v.SetDefault("log_level", "info")
	v.SetDefault("log_file", "/var/log/itechsmart/agent.log")
	
	// Security
	v.SetDefault("tls_enabled", true)
	v.SetDefault("certificate_pinning", true)
	
	// Product integration
	v.SetDefault("ninja_enabled", true)
	v.SetDefault("ninja_url", "https://ninja.itechsmart.dev")
	v.SetDefault("enterprise_enabled", true)
	v.SetDefault("enterprise_url", "https://enterprise.itechsmart.dev")
	
	// Data retention
	v.SetDefault("metrics_retention_days", 30)
	v.SetDefault("logs_retention_days", 90)
}

// Validate validates the configuration
func (c *Config) Validate() error {
	if c.ServerURL == "" {
		return fmt.Errorf("server_url is required")
	}
	
	if c.APIKey == "" {
		return fmt.Errorf("api_key is required")
	}
	
	if c.WebSocketURL == "" {
		return fmt.Errorf("websocket_url is required")
	}
	
	// Validate intervals
	if c.SystemMetricsInterval < 10 {
		return fmt.Errorf("system_metrics_interval must be at least 10 seconds")
	}
	
	if c.HeartbeatInterval < 30 {
		return fmt.Errorf("heartbeat_interval must be at least 30 seconds")
	}
	
	return nil
}

// generateRandomID generates a random ID for the agent
func generateRandomID() string {
	// Simple random ID generation
	// In production, use a more robust method
	return fmt.Sprintf("%d", os.Getpid())
}